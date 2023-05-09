"""
billboard rock 100 playlist
"""
import billboard
from datetime import datetime, timedelta


def unique_rock_tracks_generator():
    chart = billboard.ChartData("rock-songs")
    red_tracks = set()
    while len(red_tracks) < 100:
        cdate = chart.date
        date_format = "%Y-%m-%d"
        dtObj = datetime.strptime(cdate, date_format)
        n = 7
        previous_Date = dtObj - timedelta(days=n)
        top_track = chart[0]
        duplicate = top_track.title in red_tracks
        if not duplicate:
            red_tracks.add(top_track.title)
            yield top_track
        chart = billboard.ChartData("rock-songs", date=previous_Date.date())
    raise StopIteration


for track in unique_rock_tracks_generator():
    print(track)
