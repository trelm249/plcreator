""" generate a playlist of the billboard hot 100 of the 70s """
from pathlib import Path
from tinytag import TinyTag
from os import listdir
import multiprocessing
import time


start = time.perf_counter()
chart_list = listdir(Path.home().joinpath('plcharts'))

""" build the local tracks dictionary """
file_array = []
bb_array = []
gh_array = []
search_path = Path("../").rglob("*.[mf][4l][a]*")
for f_path in search_path:
    if (
        "Billboard Hits" in str(f_path)
       ):
        tag = TinyTag.get(str(f_path))
        tag_album = str.lower(tag.album)
        tag_artist = str.lower(tag.artist)
        tag_title = str.lower(tag.title)
        bb_array.append(
            {
                "f_path": f_path,
                "tag_title": tag_title,
                "tag_artist": tag_artist,
                "tag_album": tag_album,
            }
        )
    elif (
        "The Best of " in str(f_path)
        and "Greatest Hits" in str(f_path)
       ):
        tag = TinyTag.get(str(f_path))
        tag_album = str.lower(tag.album)
        tag_artist = str.lower(tag.artist)
        tag_title = str.lower(tag.title)
        gh_array.append(
            {
                "f_path": f_path,
                "tag_title": tag_title,
                "tag_artist": tag_artist,
                "tag_album": tag_album,
            }
        )    
    elif (
        "Iron Maiden-A Real" not in str(f_path)
        and "Iron Maiden-Live" not in str(f_path)
        and "Classical Conspiracy" not in str(f_path)
        and "Instrumental" not in str(f_path)
        and "Ozzy Osbourne-Tribute" not in str(f_path)
        and "Magnification" not in str(f_path)
        and "Disc 2 - Live" not in str(f_path)
        and "Demo" not in str(f_path)
        and "Mix" not in str(f_path)
        and "Perception-" not in str(f_path)
        and "-We." not in str(f_path)
        and "Live B-" not in str(f_path)
        and "Live At " not in str(f_path)
        and "Live On King " not in str(f_path)
        and "Intermission -" not in str(f_path)
        and "Evil-2-" not in str(f_path)
        and "Evil-02-" not in str(f_path)
        and "Heart-02-" not in str(f_path)
        and "Line-02-" not in str(f_path)
        and "game-ost" not in str(f_path)
       ):
        tag = TinyTag.get(str(f_path))
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

def gen_pl(item):
    chart = item[:-4]
    print(chart)
    global file_array
    file_array.reverse()
    chart_file = (Path.home().joinpath('plcharts', item))
    this_playlist = open(f"{chart}.m3u", "a", encoding="utf-8")
    with open(chart_file, "r") as source_file:
        for line in source_file:
            line_split = line.split(",")
            line_artist = str.lower(line_split[0])
            line_title = str.lower(line_split[1])
            for tr_path in file_array:
                if (
                    tr_path["tag_artist"] in line_artist
                    and tr_path["tag_title"] in line_title
                    and " live " not in tr_path["tag_album"]
                ):
                    this_playlist.write(str(tr_path["f_path"]) + "\n")
                    break


if __name__ == "__main__":
    for item in chart_list:
        gen_pl(item)
    finish = time.perf_counter()
    print(f"It took {finish-start: .2f} second(s) to finish.")
