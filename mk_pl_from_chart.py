""" generate a playlist of the billboard hot 100 of the 70s """
from pathlib import Path
from tinytag import TinyTag
from os import listdir
import time

start = time.perf_counter()

#this_playlist = open(f"{current_chart}.m3u", "a", encoding="utf-8")

""" build the local tracks dictionary """
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
""" iterate through the chart file """
chart_list = listdir(Path.home().joinpath('plcharts'))
print(chart_list)

for item in chart_list:
   chart = item[:-4]
   print(chart)
"""
with open("greatest-songs-of-the-70s.csv", "r") as source_file:
    for line in source_file:
        line_split = line.split(",")
        line_artist = str.lower(line_split[0])
        line_title = str.lower(line_split[1])
        for tr_path in file_array:
            if (
                tr_path["tag_artist"] in line_artist
                and tr_path["tag_title"] in line_title
                and "live" not in tr_path["tag_album"]
            ):
                this_playlist.write(str(tr_path["f_path"]) + "\n")
                break
"""
finish = time.perf_counter()
print(f"It took {finish-start: .2f} second(s) to finish.")
