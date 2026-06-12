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

Curation decisions are focused on:

- year released
- popularity based on airplay and purchases as tracked by applicable charts
- decade defining and cultural significance.

### By Genre

Curation decisions are focused on:

- seen as defining the genre 
- popularity based on airplay and purchases as tracked by applicable charts
- influence within the genre
- tracks the cross into the genre from genre adjacent groups
- notable deep tracks are welcome

### Special Collections
- `cathedrals-and-cataclysms.csv` - Curated thematic collection

## Usage

1. Edit or create a CSV file with your desired artist and track combinations
2. Ensure each line follows the format: `Artist Name,Track Title`
3. Copy the CSV to `~/plcharts/` (the directory `mk_pl_from_chart.py` reads from)
4. Run `python mk_pl_from_chart.py` from your playlists directory to generate `.m3u` files
5. Import the generated playlist into your preferred music player

## File Naming Convention

CSV filenames should clearly indicate the purpose or theme of the playlist they represent.
