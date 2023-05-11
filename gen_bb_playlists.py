"""
get billboard playlist
"""
from pathlib import Path
from billboard import ChartData
from tinytag import TinyTag
import multiprocessing
import time


# Define Charts Identifiers
c_Ident = [
    "greatest-billboards-top-songs-80s",
    "greatest-billboards-top-songs-90s",
    "greatest-of-all-time-mainstream-rock-songs",
    "greatest-alternative-songs",
    "greatest-country-songs",
    "jazz-songs",
]


def gen_chart(in_chart):
    """cycling through gathering the billboard chart from the web to parse"""
    print(in_chart)
    the_chart = ChartData(in_chart)
    print(the_chart.title)
    this_playlist = open(f"{in_chart}.m3u", "a", encoding="utf-8")
    """ iterate and find track paths for the playlist and store in an array to
    query iteratively"""
    file_array = []
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
        file_array.append(
            {
                "f_path": f_path,
                "tag_title": tag_title,
                "tag_artist": tag_artist,
                "tag_album": tag_album,
            }
        )
    for track in range(len(the_chart)):
        song = the_chart[track]
        track_title = song.title
        track_artist = song.artist
        for tr_path in file_array:
            """iterate through list"""
            tr_artist = str.lower(track_artist)
            """ exclude live albums """
            if (
                tr_path["tag_artist"] in tr_artist
                and str.lower(track_title) in tr_path["tag_title"]
                and "live" not in tr_path["tag_album"]
            ):
                """write the relative track path to the playlist"""
                this_playlist.write(str(tr_path["f_path"]) + "\n")
                break


if __name__ == "__main__":
    start = time.perf_counter()
    processes = [
        multiprocessing.Process(target=gen_chart, args=[in_Chart])
        for in_Chart in c_Ident
    ]
    for process in processes:
        process.start()
    for process in processes:
        process.join()
    finish = time.perf_counter()
    print(f"It took {finish-start: .2f} second(s) to finish")
