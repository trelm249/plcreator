"""
get billboard playlist
"""
from pathlib import Path
from billboard import ChartData
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
    chart_file = Path.home().joinpath('plcharts', f"{in_chart}.csv")
    this_playlist = open(chart_file, "a", encoding="utf-8")
    """ iterate and find track paths for the playlist and store in an array to
    query iteratively"""
    for track in range(len(the_chart)):
        song = the_chart[track]
        track_title = song.title
        track_artist = song.artist
        this_playlist.write(str.lower(track_artist) + "," + str.lower(track_title) + "\n")


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
