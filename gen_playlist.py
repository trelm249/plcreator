"""
get billboard playlist
"""
from billboard import ChartData

c_Dec = ["80s", "90s"]

for chart in c_Dec:
    print(chart)
    which_Chart = f"greatest-billboards-top-songs-{chart}"
    the_Chart = ChartData(which_Chart)
    print(the_Chart.title)
    with open(f"{which_Chart}.py", "a") as file:
        for track in range(0, 499):
            song = the_Chart[track]
            track_Data = song.title + ", " + song.artist + "\n"
            file.write(track_Data)
