"""
generate music playlists from the music library (Output to CWD)
"""
import time
from pathlib import Path
from tinytag import TinyTag
from multiprocessing import Pool, cpu_count
import sys
import csv
import re
import unicodedata

# --- Configuration ---
# Set the root directory of your music library
MUSIC_ROOT = Path("../")
# Set the directory containing your chart files (e.g., .csv files)
CHART_DIR = Path.home().joinpath('plcharts')
# MODIFIED: Set the output directory to the current working directory
OUTPUT_DIR = Path.cwd() 
# Add any part of a path you want to exclude from the library scan
# Using a set is faster for lookups.
EXCLUSION_PATTERNS = {
    "Iron Maiden-A Real", "Iron Maiden-Live", "Classical Conspiracy", "Instrumental",
    "Ozzy Osbourne-Tribute", "Magnification", "Disc 2 - Live", "Demo", "Mix",
    "Perception-", "-We.", "Live B-", "Live At ", "Live On King ", "Intermission -",
    "Evil-2-", "Evil-02-", "Heart-02-", "Line-02-", "game-ost", " live ",
    "Saints & Sinners", "Armageddon_", "Halloween Jams-", "Halloween-01",
    "Park-Live","Park-One", "U2-Under", "U2-Live", "1980-1990", "boxed set",
    "Apollo-Live", "Symphony-02", "Nightwish-Showtime", "Beautiful-03",
    "Beautiful-02", "Glen Frey Live"
}

_ARTICLES = {"the", "a", "an"}
_PAREN_RE = re.compile(r"[\(\[].*?[\)\]]")
_FEAT_RE = re.compile(r"\b(featuring|feat|ft)\b")
_NON_ALNUM_RE = re.compile(r"[^a-z0-9]+")

def normalize_text(text: str) -> str:
    """
    Normalize an artist or title so chart spellings can match audio tags.
    Folds accents, treats '&' as 'and', drops parenthetical/bracketed
    qualifiers, unifies featured-artist markers, and ignores punctuation
    and articles ('the', 'a', 'an').
    """
    text = unicodedata.normalize("NFKD", text)
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    text = text.lower().replace("&", " and ")
    text = _PAREN_RE.sub(" ", text)
    text = _FEAT_RE.sub(" feat ", text)
    text = _NON_ALNUM_RE.sub(" ", text)
    return " ".join(word for word in text.split() if word not in _ARTICLES)

_LIVE_TITLE_RE = re.compile(
    r"[\(\[]\s*live\b"                                       # (live...), [live...]
    r"|\blive\s+(?:version|at|from|in|on|recording|session)\b"
    r"|\s[-\u2013]\s*live\b"                                 # " - live"
)
_LIVE_ALBUM_RE = re.compile(
    r"\blive\b\s*$"                                          # "... Live"
    r"|^\s*live\s*(?:[!\-\u2013/]|\d|$)"                     # "Live", "Live!", "Live 1975"
    r"|\blive\s+(?:at|from|on|in)\b"                         # "Live at/from/on/in ..."
)

def is_live(album: str, title: str) -> bool:
    """
    Return True if the album or title marks the track as a live recording.
    Deliberately avoids matching words like 'alive' or song titles such as
    'Live To Tell', 'Live and Let Die', or 'Wanted Dead Or Alive'.
    """
    album = (album or "").lower()
    title = (title or "").lower()
    if " live " in album:
        return True
    return bool(_LIVE_ALBUM_RE.search(album) or _LIVE_TITLE_RE.search(title))

def get_album_priority(album_name: str) -> int:
    """
    Assigns a priority score to a track based on its album name.
    Lower scores are higher priority.
    - 0: Studio Album (Default)
    - 1: Greatest Hits / Best Of
    - 2: Billboard Hits
    """
    lower_album = album_name.lower()
    if 'billboard ' in lower_album or 'show and tell' in lower_album or 'right here, right now' in lower_album or 'alchemy' in lower_album:
        return 2
    if 'greatest hits' in lower_album or 'best of' in lower_album or 'red, white' in lower_album or 'platinum hits' in lower_album or 'essential' in lower_album:
        return 1
    return 0 # Default priority for studio albums

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

        tag = TinyTag.get(path_str)
        # 2. Ensure essential tags exist
        if not tag.artist or not tag.title:
            return None

        album = str.lower(tag.album or "")
        title = str.lower(tag.title)
        live = is_live(album, title)
        return {
            "f_path": path_str,
            "artist": str.lower(tag.artist),
            "title": title,
            "album": album,
            "priority": get_album_priority(album) + (100 if live else 0),
            "live": live
        }
    except Exception:
        # Gracefully handle any errors from TinyTag or file system
        return None

def build_music_lookup(root_path: Path):
    """
    Scans the music library in parallel and builds a fast lookup dictionary.
    If a duplicate song is found, it keeps the one with the highest priority (lowest score).
    """
    print("🔎 Scanning for music files...")
    files_to_process = list(root_path.rglob("*.[mf][4l][a]*"))
    print(f"Found {len(files_to_process)} potential files. Reading tags (using {cpu_count()} cores)...")

    music_lookup = {}
    with Pool(processes=cpu_count()) as pool:
        results = pool.map(process_file, files_to_process)

    print("✅ Tag reading complete. Building prioritized library lookup table...")
    for track_data in results:
        if track_data:
            key = (track_data["artist"], track_data["title"])
            
            if key in music_lookup:
                if track_data["priority"] < music_lookup[key]["priority"]:
                    music_lookup[key] = track_data
            else:
                music_lookup[key] = track_data

    # Add normalized alias keys so chart spellings can match tag spellings.
    for track_data in list(music_lookup.values()):
        alias_artist = normalize_text(track_data["artist"])
        alias_title = normalize_text(track_data["title"])
        if not alias_artist and not alias_title:
            continue
        alias_key = ("~norm~", alias_artist, alias_title)
        existing = music_lookup.get(alias_key)
        if existing is None or track_data["priority"] < existing["priority"]:
            music_lookup[alias_key] = track_data

    return music_lookup

def generate_playlist(args):
    """
    Worker function to generate a single M3U playlist from a chart file.
    """
    chart_path, music_lookup = args
    playlist_name = chart_path.stem
    # MODIFIED: Use the OUTPUT_DIR for the playlist file path
    playlist_file_path = OUTPUT_DIR / f"{playlist_name}.m3u" 
    
    sys.stdout.write(f"🎧 Generating playlist: {playlist_name}.m3u\n")
    
    found_tracks = []
    seen_paths = set()
    try:
        with open(chart_path, "r", encoding="utf-8") as source_file:
            chart_reader = csv.reader(source_file)
            for row in chart_reader:
                try:
                    line_artist, line_title = row[0].strip(), row[1].strip()

                    track = music_lookup.get((line_artist.lower(), line_title.lower()))
                    if track is None:
                        track = music_lookup.get((
                            "~norm~",
                            normalize_text(line_artist),
                            normalize_text(line_title),
                        ))

                    if track and not track.get("live"):
                        f_path = track["f_path"]
                        if f_path not in seen_paths:
                            seen_paths.add(f_path)
                            found_tracks.append(f_path)
                except IndexError:
                    continue
        
        if found_tracks:
            with open(playlist_file_path, "w", encoding="utf-8") as f_out:
                f_out.write("\n".join(found_tracks) + "\n")
                
    except Exception as e:
        sys.stderr.write(f"Error processing {chart_path.name}: {e}\n")


def main():
    """Main function to orchestrate the playlist generation."""
    start = time.perf_counter()
    
    music_library = build_music_lookup(MUSIC_ROOT)
    print(f"📚 Library built with {len(music_library)} prioritized unique tracks.\n")
    
    chart_files = list(CHART_DIR.glob('*.csv'))
    if not chart_files:
        print(f"No chart files (.csv) found in {CHART_DIR}. Exiting.")
        return

    # Create the output directory if it doesn't exist
    OUTPUT_DIR.mkdir(exist_ok=True)
    print(f"Playlists will be saved to: {OUTPUT_DIR}\n")

    tasks = [(chart, music_library) for chart in chart_files]
    
    print(f"Starting playlist generation for {len(chart_files)} charts (using {cpu_count()} cores)...")
    with Pool(processes=cpu_count()) as pool:
        pool.map(generate_playlist, tasks)
        
    finish = time.perf_counter()
    print(f"\n✨ All done! Finished in {finish - start:.2f} second(s).")


if __name__ == "__main__":
    main()
