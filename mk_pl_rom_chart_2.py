"""
generate music playlists from the music library (Optimized Version for CSV)
"""
import time
from pathlib import Path
from tinytag import TinyTag
from multiprocessing import Pool, cpu_count
import sys
import csv  # MODIFIED: Import the csv module

# --- Configuration ---
# Set the root directory of your music library
MUSIC_ROOT = Path("../")
# Set the directory containing your chart files (e.g., .csv files)
CHART_DIR = Path.home().joinpath('plcharts')
# Add any part of a path you want to exclude from the library scan
# Using a set is faster for lookups.
EXCLUSION_PATTERNS = {
    "Iron Maiden-A Real", "Iron Maiden-Live", "Classical Conspiracy", "Instrumental",
    "Ozzy Osbourne-Tribute", "Magnification", "Disc 2 - Live", "Demo", "Mix",
    "Perception-", "-We.", "Live B-", "Live At ", "Live On King ", "Intermission -",
    "Evil-2-", "Evil-02-", "Heart-02-", "Line-02-", "game-ost", " live "
}

def process_file(f_path: Path):
    """
    Worker function to read tags from a single music file.
    Returns a dictionary of track info or None if it should be skipped.
    """
    try:
        path_str = str(f_path)
        # 1. Fast exclusion check
        if any(p in path_str for p in EXCLUSION_PATTERNS):
            return None

        tag = TinyTag.get(path_str, ignore_errors=True)
        # 2. Ensure essential tags exist
        if not tag.artist or not tag.title:
            return None

        return {
            "f_path": path_str,
            "artist": str.lower(tag.artist),
            "title": str.lower(tag.title),
            "album": str.lower(tag.album or ""),  # Handle cases where album tag is None
        }
    except Exception:
        # Gracefully handle any errors from TinyTag or file system
        return None

def build_music_lookup(root_path: Path):
    """
    Scans the music library in parallel and builds a fast lookup dictionary.
    The dictionary key is (artist, title) for O(1) access.
    """
    print("🔎 Scanning for music files...")
    # Find all potential files first
    files_to_process = list(root_path.rglob("*.[mf][4l][a]*"))
    print(f"Found {len(files_to_process)} potential files. Reading tags (using {cpu_count()} cores)...")

    music_lookup = {}
    # Use a multiprocessing pool to read file tags in parallel
    with Pool(processes=cpu_count()) as pool:
        # pool.map distributes the 'files_to_process' list among worker processes
        results = pool.map(process_file, files_to_process)

    print("✅ Tag reading complete. Building library lookup table...")
    for track_data in results:
        if track_data:
            key = (track_data["artist"], track_data["title"])
            # Only add the first encountered version of a track
            if key not in music_lookup:
                music_lookup[key] = {
                    "f_path": track_data["f_path"],
                    "album": track_data["album"]
                }
    return music_lookup

def generate_playlist(args):
    """
    Worker function to generate a single M3U playlist from a chart file.
    Designed to be called by a multiprocessing Pool.
    """
    chart_path, music_lookup = args  # Unpack arguments
    playlist_name = chart_path.stem
    playlist_file_path = CHART_DIR / f"{playlist_name}.m3u"
    
    sys.stdout.write(f"🎧 Generating playlist: {playlist_name}.m3u\n")
    
    found_tracks = []
    try:
        with open(chart_path, "r", encoding="utf-8") as source_file:
            # MODIFIED: Use a csv.reader for robust parsing
            chart_reader = csv.reader(source_file)
            for row in chart_reader:
                try:
                    # Assumes artist is in the first column, title in the second
                    line_artist, line_title = row[0].strip(), row[1].strip()
                    search_key = (str.lower(line_artist), str.lower(line_title))
                    
                    # This is the O(1) lookup - fast and efficient!
                    track = music_lookup.get(search_key)
                    
                    if track and " live " not in track["album"]:
                        found_tracks.append(track["f_path"])
                except IndexError:
                    # Skip empty or malformed rows in the CSV file
                    continue
        
        # Write all found tracks to the playlist file at once
        if found_tracks:
            with open(playlist_file_path, "w", encoding="utf-8") as f_out:
                f_out.write("\n".join(found_tracks) + "\n")
                
    except Exception as e:
        sys.stderr.write(f"Error processing {chart_path.name}: {e}\n")


def main():
    """Main function to orchestrate the playlist generation."""
    start = time.perf_counter()
    
    # 1. Build the music library lookup table efficiently
    music_library = build_music_lookup(MUSIC_ROOT)
    print(f"📚 Library built with {len(music_library)} unique tracks.\n")
    
    # 2. Get the list of chart files to process
    # MODIFIED: Look for .csv files instead of .txt
    chart_files = list(CHART_DIR.glob('*.csv'))
    if not chart_files:
        print("No chart files (.csv) found in the specified directory. Exiting.")
        return

    # 3. Prepare arguments for parallel processing
    tasks = [(chart, music_library) for chart in chart_files]
    
    # 4. Generate all playlists in parallel
    print(f"Starting playlist generation for {len(chart_files)} charts (using {cpu_count()} cores)...")
    with Pool(processes=cpu_count()) as pool:
        pool.map(generate_playlist, tasks)
        
    finish = time.perf_counter()
    print(f"\n✨ All done! Finished in {finish - start:.2f} second(s).")


if __name__ == "__main__":
    main()