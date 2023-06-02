"""
billboard rock 100 playlist
"""
from pathlib import Path
from tinytag import TinyTag
import multipprocessing
import time
import billboard

bbchart = [
    "hot-rock-songs",
    "hot-100-songs",
]

cyears = [
    "2022",
    "2021",
    "2020",
    "2019",
    "2018",
    "2017",
    "2016",
    "2015",
    "2014",
    "2013",
    "2012",
    "2011",
    "2010",
    "2009",
    "2008",
    "2007",
    "2006",
]


def year_end_tracks_generator(current_chart, current_year):
    chart = billboard.ChartData(current_chart, year=current_year)
    red_tracks = set()
    this_playlist = open(f"{current_chart}.m3u", "a", encoding="utf-8")
    file_array = []
    search_path = Path("../").rglob("*.[mf][4l][a]*")
    for f_path in search_path:
        tag = TinyTag.get(f_path)
        tag_album = str.lower(tag.album)
        tag_artist = str.lower(tag.artist)
        tag_title = str.lower(tag.title)
        file_array.append(
            {
                "f_path": f_path,
                "tag_title": tag_title,
                "tag_artist": tag_artist,
                "tag_album": tag_album,
            }
        )
    for i in range(25):
        this_track = chart[i]
        duplicate = this_track.title in red_tracks
        if not duplicate:
            red_tracks.add(this_track.title)
            track_title = this_track.title
            track_artist = this_track.artist
            for tr_path in file_array:
                tr_artist = str.lower(track_artist)
                if (
                    tr_path["tag_artist"] in tr_artist
                    and str.lower(track_title) in tr_path["tag_title"]
                ):
                    this_playlist.write(str(str(tr_path["f_path"]) + "\n"))
                    break
            yield this_track
    this_playlist.close()


if __name__ == "__main__":
    start = time.perf_counter()
    for current_chart in bbchart:
        for current_year in cyears:
            for track in year_end_tracks_generator(
                current_chart, current_year
            ):
                print(track)
    finish = time.perf_counter()
    print(f"It took {finish-start: 2f} second(s) to finish.")
