"""
get billboard playlist
"""
from billboard import ChartData
from tinytag import TinyTag
from pathlib import Path
from multiprocessing import Pool
from concurrent.futures import ThreadPoolExecutor

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
    with ThreadPoolExecutor(max_workers=4) as tpe:
        for track in range(len(the_Chart)):
            song = the_Chart[track]
            track_title = song.title
            track_artist = song.artist
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
                    pl.write(str(path) + "\n")
                    break

if __name__ == "__main__":
    mpool = Pool(16)
    results = mpool.map(gen_chart, c_Ident)
    results = []
    for in_Chart in c_Ident:
        results.append(mpool.apply_async(gen_chart(in_Chart)))
