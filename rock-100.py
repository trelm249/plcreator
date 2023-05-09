"""
billboard rock 100 playlist
"""
import billboard
from datetime import datetime, timedelta


def unique_rock_tracks_generator():
    chart = billboard.ChartData("rock-songs")
    red_tracks = set()
    this_playlist = open("rock_100.m3u", "a", encoding="utf-8")
    while len(red_tracks) < 100:
        cdate = chart.date
        date_format = "%Y-%m-%d"
        dtObj = datetime.strptime(cdate, date_format)
        n = 10
        previous_Date = dtObj - timedelta(days=n)
        top_track = chart[0]
        duplicate = top_track.title in red_tracks
        if not duplicate:
            red_tracks.add(top_track.title)
            this_playlist.write(str(top_track.title) + " ; " + str(top_track.artist) + "\n")
            yield top_track
        chart = billboard.ChartData("rock-songs", date=previous_Date.date())
    this_playlist.close()
    raise StopIteration


for track in unique_rock_tracks_generator():
    print(track)
