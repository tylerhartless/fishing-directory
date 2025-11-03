"""
Parse all Texas city fishing location PDFs (Houston, Austin, DFW, San Antonio)

This script extracts fishing location data from TPWD city-specific PDF guides.
"""

import sys
import os
import json
import re

try:
    import pypdf
except ImportError:
    print("[ERROR] pypdf not installed. Install with: pip install pypdf")
    sys.exit(1)

# Import the parser function from houston parser
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from parse_houston_pdf import extract_text_from_pdf, parse_fishing_locations


def parse_all_city_pdfs():
    """Parse all city fishing PDFs"""

    pdfs = {
        'houston': '../../raw-data/houston_fishing.pdf',
        'austin': '../../raw-data/austin_fishing.pdf',
        'dfw': '../../raw-data/dfw_fishing.pdf',
        'san_antonio': '../../raw-data/san_antonio_fishing.pdf'
    }

    all_locations = []

    for city_name, pdf_path in pdfs.items():
        if not os.path.exists(pdf_path):
            print(f"[WARN] {city_name.title()} PDF not found at: {pdf_path}")
            continue

        print("="*70)
        print(f"Parsing {city_name.title()} PDF")
        print("="*70)
        print()

        # Extract text
        text_pages = extract_text_from_pdf(pdf_path)
        if not text_pages:
            print(f"[ERROR] Could not extract text from {city_name} PDF")
            continue

        print(f"[OK] Extracted text from {len(text_pages)} pages")

        # Parse locations
        locations = parse_fishing_locations(text_pages)

        # Add city tag to each location
        for loc in locations:
            loc['source_city'] = city_name

        all_locations.extend(locations)

        print(f"[OK] Found {len(locations)} locations in {city_name.title()}")
        print()

    return all_locations


def main():
    print("="*70)
    print("Parsing All Texas City Fishing Location PDFs")
    print("="*70)
    print()

    all_locations = parse_all_city_pdfs()

    if all_locations:
        output_path = "../../raw-data/all_city_fishing_spots.json"
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(all_locations, f, indent=2)

        print()
        print("="*70)
        print("Summary")
        print("="*70)
        print(f"Total locations extracted: {len(all_locations)}")

        # Count by city
        from collections import Counter
        city_counts = Counter(loc['source_city'] for loc in all_locations)
        for city, count in sorted(city_counts.items()):
            print(f"  {city.title():15} {count:3} locations")

        print()
        print(f"[OK] Saved to: {output_path}")
        print("="*70)
    else:
        print("[WARN] No locations parsed")

    return 0


if __name__ == "__main__":
    sys.exit(main())
