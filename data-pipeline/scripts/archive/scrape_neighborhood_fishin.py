"""
Scrape Texas Neighborhood Fishin' Lakes from TPWD website

The data is embedded in JavaScript as Leaflet markers, not GeoJSON.
This script extracts the marker data and converts it to GeoJSON.

Usage:
    python scripts/scrape_neighborhood_fishin.py [--output OUTPUT]
"""

import requests
import re
import json
import sys


def scrape_neighborhood_fishin():
    """Scrape neighborhood fishing lakes from TPWD website"""

    url = "https://tpwd.texas.gov/fishboat/fish/programs/neighborhood-fishin/include/nf-mapcode.min.js"

    print("="*60)
    print(f"Scraping Neighborhood Fishin' Lakes")
    print("="*60)
    print()
    print(f"Fetching: {url}")

    response = requests.get(url, headers={
        'User-Agent': 'FishingDirectoryBot/1.0 (Educational fishing access directory)'
    })
    response.raise_for_status()

    js_content = response.text
    print("[OK] Downloaded JavaScript file")

    # Simpler approach: split into marker chunks and extract each piece separately
    # Each marker follows pattern: variableName=markers[markers.push(L.marker([lat,lon],{...title:"..."...}).bindPopup('...'))-1]

    # Find all marker chunks
    marker_chunks = re.split(r'(?==markers\[markers\.push)', js_content)

    matches = []
    for chunk in marker_chunks:
        # Extract coordinates
        coord_match = re.search(r'L\.marker\(\[([0-9.-]+),([0-9.-]+)\]', chunk)
        if not coord_match:
            continue

        lat, lon = coord_match.groups()

        # Extract title (contains "Name, City")
        title_match = re.search(r'title:"([^"]+)"', chunk)
        if not title_match:
            continue

        title = title_match.group(1)

        # Extract name from popup <h3>
        name_match = re.search(r'<h3>([^<]+)</h3>', chunk)
        name = name_match.group(1) if name_match else title.split(',')[0].strip()

        # Extract address and size - try multiple patterns
        address = ''
        size_line = ''

        # Pattern 1: <p>address<br/>size</p>
        p1_match = re.search(r'<p>([^<]+)<br/>([0-9.]+\s*acres?)</p>', chunk, re.IGNORECASE)
        if p1_match:
            address = p1_match.group(1).strip()
            size_line = p1_match.group(2)
        else:
            # Pattern 2: <p>address<br/>city<br/>size</p>
            p2_match = re.search(r'<p>([^<]+)<br/>([^<]+)<br/>([0-9.]+\s*acres?)</p>', chunk, re.IGNORECASE)
            if p2_match:
                address = p2_match.group(1).strip()
                size_line = p2_match.group(3)

        matches.append((lat, lon, title, name, address, size_line))

    print(f"[OK] Found {len(matches)} neighborhood fishing lakes")
    print()

    features = []
    for i, match in enumerate(matches, 1):
        lat, lon, title, name, address, size = match

        # Extract city from title (e.g., "Medical Center South, Amarillo" -> "Amarillo")
        city_match = re.search(r',\s*([^,]+)$', title)
        city = city_match.group(1).strip() if city_match else ''

        # Extract acreage (e.g., "7 acres" -> "7")
        size_match = re.search(r'([0-9.]+)\s*acre', size)
        acreage = size_match.group(1) if size_match else None

        # Clean name
        clean_name = name.strip()

        print(f"[{i}] {clean_name} ({city}) - {acreage} acres")

        feature = {
            "type": "Feature",
            "properties": {
                "ID": f"NF{i:03d}",
                "name": clean_name,
                "city": city,
                "address": address.strip(),
                "size": acreage,
                "program": "Neighborhood Fishin'"
            },
            "geometry": {
                "type": "Point",
                "coordinates": [float(lon), float(lat)]
            }
        }

        features.append(feature)

    geojson = {
        "type": "FeatureCollection",
        "features": features
    }

    return geojson


def main():
    import argparse
    import os

    parser = argparse.ArgumentParser(description='Scrape Texas Neighborhood Fishin\' Lakes')
    parser.add_argument('--output', help='Output JSON file path', default='../../raw-data/neighborhood_fishin_lakes.json')
    args = parser.parse_args()

    try:
        geojson = scrape_neighborhood_fishin()

        # Save to file
        output_path = args.output
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(geojson, f, indent=2)

        print()
        print("="*60)
        print("[OK] Saved GeoJSON to:", output_path)
        print(f"  Features: {len(geojson['features'])}")
        print("="*60)

        return 0

    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
