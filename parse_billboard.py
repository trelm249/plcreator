'''Fetch and parse Billboard Year-End Hot 100 from Wikipedia for 1980–1989.'''

import urllib.request
import re
import json


def _clean(s):
    s = s.replace('&amp;', '&').replace('&#39;', "'").replace('&quot;', '"')
    s = re.sub(r'\s+', ' ', s).strip()
    return s.lower()


def fetch_year(year):
    url = f'https://en.wikipedia.org/wiki/Billboard_Year-End_Hot_100_singles_of_{year}'
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=15) as resp:
            content = resp.read().decode('utf-8')
    except Exception as e:
        print(f'  Error fetching {year}: {e}')
        return None

    # Find the wikitable section
    m = re.search(
        r'<table\s+class="wikitable sortable"[^>]*>.*?</table>',
        content,
        re.DOTALL | re.IGNORECASE
    )
    if not m:
        return None
    table_html = m.group()

    # Extract rows
    rows = re.findall(r'<tr[^>]*>(.*?)</tr>', table_html, re.DOTALL)
    if not rows:
        return None

    result = []
    pending_artist = None  # For rowspan tracking

    for row in rows:
        cells = re.findall(r'<(?:td|th)[^>]*>(.*?)</(?:td|th)>', row, re.DOTALL)
        if not cells:
            continue

        # Check if first row (headers)
        if re.search(r'<th', row):
            continue

        # Clean cells
        cleaned = []
        for c in cells:
            # Remove HTML tags but keep their inner text
            text = re.sub(r'<[^>]+>', '', c)
            text = text.strip().strip('" ')
            text = re.sub(r'\s+', ' ', text)
            cleaned.append(text)

        if len(cleaned) < 2:
            continue

        rank_str = cleaned[0]
        title = cleaned[1] if len(cleaned) > 1 else ''
        artist = cleaned[2] if len(cleaned) > 2 else (pending_artist or '')

        # Check for rowspan on artist
        artist_cell = re.search(r'<td[^>]*rowspan\s*=\s*["\']?(\d+)["\']?[^>]*>', row)
        if artist_cell and len(cleaned) >= 3:
            pending_artist = artist

        # Try to extract rank
        m2 = re.match(r'(\d+)', rank_str)
        if not m2:
            continue
        rank = int(m2.group(1))

        result.append((rank, _clean(title), _clean(artist)))

    return result if result else None


def main():
    result = {}
    for year in range(1980, 1990):
        data = fetch_year(year)
        if data:
            result[year] = data
            print(f'{year}: {len(data)} songs')
        else:
            print(f'{year}: FAILED')

    print()
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
