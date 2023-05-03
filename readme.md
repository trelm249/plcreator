# README
> A python script to generate a playlist from a few of the Billboard charts.

## purpose
> This will generate an m3u file to create a playlist using relative paths based on Billboard charts. The idea is that the playlist reside in a playlist folder relative to the track files. This is for portability to mobile media and rsynced libraries.

## Charts referenced

- greatest-billboards-top-songs-80s
- greatest-billboards-top-songs-90s
- greatest-of-all-time-mainstream-rock-songs

## Usage and environment
> The script is run in your playlists directory and uses relative paths to build the playlists. The assumption is playlists is at the same tier as rock in the filesystem.

invoke with `python gen_bb_playlists.py`

## Roadmap
- add working multithreading to track path search
