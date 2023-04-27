"""
get billboard playlist
"""
from billboard import ChartData
from tinytag import TinyTag
from pathlib import Path

c_Ident = ["greatest-billboards-top-songs-80s", "greatest-billboards-top-songs-90s", "greatest-of-all-time-mainstream-rock-songs"]

def gen_Playlist():
    for chart in c_Ident:
        print(chart)
        which_Chart = chart
        the_Chart = ChartData(which_Chart)
        print(the_Chart.title)
        pl = open(f"{which_Chart}.m3u", "a", encoding="utf-8")
        for track in range(len(the_Chart)):
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

gen_Playlist()
