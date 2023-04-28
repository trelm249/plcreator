"""
get billboard playlist
"""
from billboard import ChartData
from tinytag import TinyTag
from pathlib import Path
from multiprocessing.dummy import Pool as ThreadPool

c_Ident = [
    "greatest-billboards-top-songs-80s",
    "greatest-billboards-top-songs-90s",
    "greatest-of-all-time-mainstream-rock-songs",
]


def gen_chart(in_Chart):
    """cycling through gathering the billboard chart from the web to parse"""
    print(in_Chart)
    the_Chart = ChartData(in_Chart)
    print(the_Chart.title)
    pl = open(f"{in_Chart}.m3u", "a", encoding="utf-8")
    """ Now searching through the filesystem under ../rock/ for songs that
        are in the chart """
    for track in range(len(the_Chart)):
        song = the_Chart[track]
        track_title = song.title
        track_artist = song.artist
        """ remove 80s compilation albums from non 80s chart searches
            Also limit searches to m4a and flac files """
        if "80s" in in_Chart:
            search_Path = Path("../rock/").rglob("*.[mf][4l][a]*")
        else:
            search_Path = Path(f"../rock/{track_artist}/").rglob(
                "*.[mf][4l][a]*"
            )
        for path in search_Path:
            tag = TinyTag.get(path)
            tag_Album = str.lower(tag.album)
            tag_Artist = str.lower(tag.artist)
            tr_Artist = str.lower(track_artist)
            if (
                tag_Artist in tr_Artist
                and str.lower(track_title) == str.lower(tag.title)
                and "live" not in tag_Album
            ):
                print(path)
                raw_src = str(path)
                pl.write(raw_src + "\n")
                """ insert a break to quit and prevent duplicate songs in the
                playlists """
                break


if __name__ == "__main__":
    pool = ThreadPool(4)
    results = pool.map(gen_chart, c_Ident)
    results = []
    for in_Chart in c_Ident:
        results.append(pool.apply_async(gen_chart(in_Chart)))
