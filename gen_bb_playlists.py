"""
get billboard playlist
"""
from billboard import ChartData
from tinytag import TinyTag
from pathlib import Path

c_Ident = [
    "greatest-billboards-top-songs-80s",
    "greatest-billboards-top-songs-90s",
    "greatest-of-all-time-mainstream-rock-songs",
]


def gen_Playlist():
""" cycling through gathering the billboard chart from the web to parse """
    for chart in c_Ident:
        print(chart)
        which_Chart = chart
        the_Chart = ChartData(which_Chart)
        print(the_Chart.title)
        pl = open(f"{which_Chart}.m3u", "a", encoding="utf-8")
        """ Now searching through the filesystem under ../rock/ for songs that
        are in the chart """
        for track in range(len(the_Chart)):
            song = the_Chart[track]
            track_title = song.title
            track_artist = song.artist
            for path in Path("../rock/").rglob("*.[mf][4l][a]*"):
                tag = TinyTag.get(path)
                tag_Album = str.lower(tag.album)
                tag_Artist = str.lower(tag.artist)
                tr_Artist = str.lower(track_artist)
                if (
                    tag_Artist in tr_Artist
                    and str.lower(track_title) == str.lower(tag.title)
                    and tag_Album.__contains__("live") == False
                ):
                    print(path)
                    raw_src = str(path)
                    src = raw_src.replace(" ", "\ ")
                    """ writing the relative path of the file to an .m3u
                    playlist """
                    pl.write(raw_src + "\n")


gen_Playlist()
