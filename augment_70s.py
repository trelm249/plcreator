"""
Augment charts/greatest-songs-1970s.csv with entries from Playback.fm
annual Top 100 Rock & Roll charts for 1970-1979.
Skips exact + normalised duplicates, appends in existing lowercase CSV format.
"""
import csv
import re
import time
import urllib.request
from html.parser import HTMLParser
from pathlib import Path

CSV_PATH = Path("charts/greatest-songs-1970s.csv")
YEARS = list(range(1970, 1980))
USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"


class PlaybackTableParser(HTMLParser):
    """Extract rank table rows from Playback.fm chart pages."""
    def __init__(self):
        super().__init__()
        self.in_tr = False
        self.in_td = False
        self.in_no = False
        self.in_song = False
        self.cols = []
        self.rows = []
        self.buf = ""

    def handle_starttag(self, tag, attrs):
        if tag == "tr":
            self.in_tr = True
            self.cols = []
        if tag == "td" and self.in_tr:
            self.in_td = True
            classes = dict(attrs).get("class", "")
            self.in_no = "no" in classes
            self.in_song = not self.in_no
            self.buf = ""

    def handle_endtag(self, tag):
        if tag == "tr" and self.in_tr:
            self.in_tr = False
            if len(self.cols) >= 2:
                self.rows.append(self.cols[:2])
        if tag == "td":
            if self.in_td and self.buf:
                self.cols.append(self.buf.strip())
            self.in_td = False
            self.in_no = False
            self.in_song = False

    def handle_data(self, data):
        if self.in_td:
            self.buf += data


def fetch_playback_chart(year):
    """Return list of (artist, title) for a given year."""
    url = f"https://playback.fm/charts/rock/{year}"
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    resp = urllib.request.urlopen(req, timeout=30)
    html = resp.read().decode("utf-8", errors="replace")

    parser = PlaybackTableParser()
    parser.feed(html)

    entries = []
    for col in parser.rows:
        raw = col[1]  # combined "title\n\n\nartist" string
        parts = [p.strip() for p in raw.split("\n") if p.strip()]
        # parts[0] is title, parts[-1] is artist
        if len(parts) >= 2:
            title = parts[0]
            artist = parts[-1]
        elif len(parts) == 1:
            title = parts[0]
            artist = col[0] if len(col) > 0 else ""
        else:
            continue

        # Clean Billboard-featured separators
        artist = re.sub(r"\s*Featuring\s+", " ft. ", artist, flags=re.I)
        artist = re.sub(r"\s*& The ", " & the ", artist)
        entries.append((artist.strip(), title.strip()))

    print(f"  Parsed {len(entries)} entries from playback.fm/charts/rock/{year}")
    return entries


# ── Normalisation ────────────────────────────────────────────────────
def norm(s):
    s = s.lower().strip()
    s = re.sub(r"[''!.?]", "", s)
    s = re.sub(r"/.*$", "", s)          # drop combined "song1/song2"
    s = re.sub(r"\s*\(.*?\)", "", s)    # drop parentheticals
    s = re.sub(r"\s*\[.*?\]", "", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def norm_artist(s):
    a = norm(s)
    a = re.sub(r"^the\s+", "", a)
    a = re.sub(r"\band\b", "&", a)
    return a


# ── Main ──────────────────────────────────────────────────────────────
def main():
    start = time.perf_counter()

    # Load existing
    raw_set = set()
    norm_set = set()
    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        for row in csv.reader(f):
            if len(row) >= 2:
                a = row[0].strip().lower()
                t = row[1].strip().lower()
                raw_set.add((a, t))
                norm_set.add((norm_artist(a), norm(t)))

    print(f"Existing entries: {len(raw_set)}")
    all_new = []
    total_seen = 0

    for year in YEARS:
        print(f"\nFetching: Playback.fm Top 100 Rock {year}")
        try:
            entries = fetch_playback_chart(year)
            total_seen += len(entries)
        except Exception as e:
            print(f"  ERROR: {e}")
            continue

        for artist, title in entries:
            a = artist.lower().strip()
            t = title.lower().strip()
            if (a, t) in raw_set:
                continue
            key = (norm_artist(a), norm(t))
            if key in norm_set:
                continue
            raw_set.add((a, t))
            norm_set.add(key)
            all_new.append((a, t))
            print(f"  + {a},{t}")

    # Append
    if all_new:
        with open(CSV_PATH, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            for artist, title in all_new:
                writer.writerow([artist, title])
        print(f"\n{'='*60}")
        print(f"Added {len(all_new)} new entries from Playback.fm rock charts")
    else:
        print(f"\n{'='*60}")
        print("No new entries found.")

    elapsed = time.perf_counter() - start
    print(f"Scanned {total_seen} entries across {len(YEARS)} years in {elapsed:.1f}s")


if __name__ == "__main__":
    main()
