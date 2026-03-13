# Music Charts Collection

A curated collection of CSV files containing music artists and tracks, designed to be processed by a Python script to generate `.m3u` playlist files.

## Overview

This repository contains music chart data organized by genre and decade. Each CSV file represents a different playlist theme and can be converted into a playable `.m3u` playlist file.

## CSV File Format

Each CSV file follows a simple format with one song per line:

```
Artist Name,Track Title
```

**Example:**
```csv
Led Zeppelin,Stairway to Heaven
Pink Floyd,Comfortably Numb
The Beatles,Hey Jude
```

## Available Playlists

### By Decade
- `greatest-songs-1960s.csv` - Greatest songs from the 1960s
- `greatest-songs-1970s.csv` - Greatest songs from the 1970s
- `greatest-songs-1980s.csv` - Greatest songs from the 1980s
- `greatest-songs-1990s.csv` - Greatest songs from the 1990s
- `greatest-songs-2000s.csv` - Greatest songs from the 2000s
- `greatest-songs-2010s.csv` - Greatest songs from the 2010s

### By Genre
- `alternative-hits.csv` - Alternative rock hits
- `greatest-classic-rock-songs.csv` - Classic rock essentials
- `greatest-metal-songs.csv` - Heavy metal classics
- `hair-band-hits.csv` - Hair metal and glam rock hits
- `prog-rock.csv` - Progressive rock masterpieces
- `prog-metal.csv` - Progressive metal tracks
- `southernBoogie.csv` - Southern rock and boogie

### Special Collections
- `cathedrals-and-cataclysms.csv` - Curated thematic collection

## Usage

1. Edit or create a CSV file with your desired artist and track combinations
2. Ensure each line follows the format: `Artist Name,Track Title`
3. Run the Python script to generate the corresponding `.m3u` playlist file
4. Import the generated playlist into your preferred music player

## File Naming Convention

CSV filenames should clearly indicate the purpose or theme of the playlist they represent.