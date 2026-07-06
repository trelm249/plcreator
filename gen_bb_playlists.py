"""
get billboard playlist
"""
from pathlib import Path
from billboard import ChartData
from tinytag import TinyTag
import time

import billboard


def _fixed_parseNewStylePage(self, soup):
    dateElement = soup.select_one("#chart-date-picker")
    if dateElement:
        self.date = dateElement["data-date"]
    self.previousDate = None
    self.nextDate = None

    awardColumnOffset = 0 if self._pageHasAwardColumn(soup) else -1

    for entrySoup in soup.select("ul.o-chart-results-list-row"):
        def getEntryAttr(which_li, selector):
            element = entrySoup.select("li")[which_li].select_one(selector)
            if element:
                return element.text.strip()
            return None

        try:
            title = getEntryAttr(3, "#title-of-a-story")
        except:
            message = "Failed to parse title"
            raise billboard.BillboardParseException(message)

        try:
            artist = getEntryAttr(3, "#title-of-a-story + span.c-label") or ""
        except:
            message = "Failed to parse artist"
            raise billboard.BillboardParseException(message)

        if artist == "":
            title, artist = artist, title

        imageElement = entrySoup.select_one("li:nth-child(2) img")
        if imageElement:
            image = imageElement.get("data-lazy-src", None)
        else:
            image = None

        try:
            rank = int(getEntryAttr(0, "span.c-label"))
        except:
            message = "Failed to parse rank"
            raise billboard.BillboardParseException(message)

        def getMeta(attribute, which_li, ifNoValue=None):
            try:
                selected = entrySoup.select_one("ul").select("li")[which_li]
                if not selected:
                    return ifNoValue
                value = selected.text.strip()
                if value == "-":
                    return ifNoValue
                else:
                    return int(value)
            except:
                message = "Failed to parse metadata value: %s" % attribute
                raise billboard.BillboardParseException(message)

        if self.date:
            peakPos = getMeta("peak", 4 + awardColumnOffset)
            lastPos = getMeta("last", 3 + awardColumnOffset, ifNoValue=0)
            weeks = getMeta("week", 5 + awardColumnOffset, ifNoValue=1)
            isNew = True if weeks == 1 else False
        else:
            peakPos = lastPos = weeks = None
            isNew = False

        entry = billboard.ChartEntry(
            title, artist, image, peakPos, lastPos, weeks, rank, isNew
        )
        self.entries.append(entry)


billboard.ChartData._parseNewStylePage = _fixed_parseNewStylePage


# Define Charts Identifiers
c_Ident = [
    "greatest-billboards-top-songs-80s",
    "greatest-billboards-top-songs-90s",
    "greatest-of-all-time-mainstream-rock-songs",
    "greatest-alternative-songs",
    "greatest-country-songs",
    "jazz-songs",
]


def build_file_db(in_chart):
    db = []
    if "country" in in_chart:
        search_path = Path("../Country/").rglob("*.[mf][4l][a]*")
    elif "jazz" in in_chart:
        search_path = Path("../Jazz/").rglob("*.[mf][4l][a]*")
    else:
        search_path = Path("../rock/").rglob("*.[mf][4l][a]*")
    for f_path in search_path:
        tag = TinyTag.get(f_path)
        tag_album = str.lower(tag.album)
        tag_artist = str.lower(tag.artist)
        tag_title = str.lower(tag.title)
        db.append(
            {
                "f_path": f_path,
                "tag_title": tag_title,
                "tag_artist": tag_artist,
                "tag_album": tag_album,
            }
        )
    return db


def gen_chart(in_chart):
    """cycling through gathering the billboard chart from the web to parse"""
    print(f"\nFetching: {in_chart}")
    the_chart = ChartData(in_chart, timeout=60)
    if not the_chart.entries:
        print(f"  WARNING: empty chart for '{in_chart}'")
        return
    print(f"  Title: {the_chart.title} ({len(the_chart)} entries)")

    with open(f"{in_chart}.m3u", "w", encoding="utf-8") as this_playlist:
        file_db = build_file_db(in_chart)
        found = 0
        for track in the_chart:
            track_title = track.title
            track_artist = track.artist
            for tr_path in file_db:
                tr_artist = str.lower(track_artist)
                if (
                    tr_artist in tr_path["tag_artist"]
                    and str.lower(track_title) in tr_path["tag_title"]
                    and "live" not in tr_path["tag_album"]
                ):
                    this_playlist.write(str(tr_path["f_path"]) + "\n")
                    found += 1
                    break
        print(f"  Matched {found}/{len(the_chart)} tracks → {in_chart}.m3u")


if __name__ == "__main__":
    start = time.perf_counter()
    for in_Chart in c_Ident:
        gen_chart(in_Chart)
    finish = time.perf_counter()
    print(f"\nIt took {finish-start: .2f} second(s) to finish")
