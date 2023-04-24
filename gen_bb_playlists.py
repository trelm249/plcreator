"""
get billboard playlist
"""
from billboard import ChartData
from tinytag import TinyTag
from pathlib import Path

c_Dec = ["80s", "90s"]

for chart in c_Dec:
    print(chart)
    which_Chart = f"greatest-billboards-top-songs-{chart}"
    the_Chart = ChartData(which_Chart)
    print(the_Chart.title)
    pl = open(f"{which_Chart}.m3u", "a", encoding="utf-8")
    for track in range(0, 499):
        song = the_Chart[track]
        track_title = song.title
        track_artist = song.artist
        for path in Path(f"../rock/{track_artist}").rglob(
            "*.[mf][4l][a]*"
        ):
            tag = TinyTag.get(path)
            album = str.lower(tag.album)
            if (
                str.lower(track_artist) == str.lower(tag.artist)
                and str.lower(track_title) == str.lower(tag.title)
                and album.__contains__("live") == False
            ):
                print(path)
                raw_src = str(path)
                src = raw_src.replace(" ", "\ ")
                pl.write(raw_src + "\n")

rock_chart = ChartData("greatest-of-all-time-mainstream-rock-songs")
pl = open("top-rock-songs-all-time.m3u", "a", encoding="utf-8")
for track in range(0, 99):
    song = rock_chart[track]
    track_title = song.title
    track_artist = song.artist
    for path in Path(f"../rock/{track_artist}").rglob(
        "*.[mf][4l][a]*"
    ):
        tag = TinyTag.get(path)
        album = str.lower(tag.album)
        if (
            str.lower(track_artist) == str.lower(tag.artist)
            and str.lower(track_title) == str.lower(tag.title)
            and album.__contains__("live") == False
        ):
            print(path)
            raw_src = str(path)
            src = raw_src.replace(" ", "\ ")
            pl.write(raw_src + "\n")
