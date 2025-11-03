"""
Parse Houston fishing locations from TPWD PDF

This script extracts fishing location data from the Houston area PDF guide.
"""

import sys
import os
import json
import re

# Try to import pypdf
try:
    import pypdf
    HAS_PYPDF = True
except ImportError:
    HAS_PYPDF = False
    print("[WARN] pypdf not installed. Trying PyPDF2...")
    try:
        import PyPDF2
        HAS_PYPDF2 = True
    except ImportError:
        HAS_PYPDF2 = False
        print("[ERROR] Neither pypdf nor PyPDF2 is installed.")
        print("Install with: pip install pypdf")
        sys.exit(1)


def extract_text_from_pdf(pdf_path):
    """Extract all text from PDF"""
    text_pages = []

    try:
        if HAS_PYPDF:
            reader = pypdf.PdfReader(pdf_path)
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    text_pages.append(text)
        else:
            with open(pdf_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages:
                    text = page.extract_text()
                    if text:
                        text_pages.append(text)

        return text_pages

    except Exception as e:
        print(f"[ERROR] Failed to extract text from PDF: {e}")
        return []


def parse_fishing_locations(text_pages):
    """
    Parse fishing locations from extracted text

    Format is:
    1. Name
       Fish species
       Address
    """
    locations = []

    full_text = "\n".join(text_pages)

    # Split by numbered entries
    # Find all instances of "number. " at the start of a line
    entries = re.split(r'\n(\d+)\.\s+', full_text)

    # entries[0] is preamble, then alternating numbers and content
    for i in range(1, len(entries), 2):
        if i+1 >= len(entries):
            break

        number = entries[i]
        content = entries[i+1]

        # Split content into lines, filter out junk (map numbers, etc.)
        lines = []
        for line in content.split('\n'):
            line = line.strip()
            if not line:
                continue
            # Skip lines that are just numbers (map markers)
            if re.match(r'^\d+$', line):
                continue
            # Skip map attribution text
            if 'Sources: Esri' in line or 'OpenStreetMap' in line or 'GIS User Community' in line:
                continue
            lines.append(line)

        # Skip if not enough lines
        if len(lines) < 2:
            continue

        # Find address line - look for numbers (street addresses start with numbers)
        # or common Texas cities, or street patterns
        address_idx = None
        for idx in range(len(lines) - 1, -1, -1):  # Work backwards
            line = lines[idx]
            # Check if line starts with a number (street address) or contains common patterns
            if re.match(r'^\d+', line) or re.search(r'(St\.|Blvd\.|Rd\.|Dr\.|Pkwy\.|Ave\.|Ln\.|Loop|Hwy|FM|TX-)', line, re.IGNORECASE):
                address_idx = idx
                break
            # Or if it ends with a Texas city name
            if re.search(r',\s*(Houston|Spring|Katy|Conroe|Cypress|Sugar Land|Missouri City|Pasadena|Tomball|Alvin|Webster|Friendswood|Baytown|Richmond|Rosenberg|Meadows Place|Pearland|Needville)\s*$', line, re.IGNORECASE):
                address_idx = idx
                break

        # If no address found, assume last line
        if address_idx is None:
            address_idx = len(lines) - 1

        # Make sure we have at least one line for name/species
        if address_idx < 1:
            continue

        # Everything before address is name and species
        # Name typically ends when we hit species keywords
        name_lines = []
        species_lines = []
        in_species = False

        for idx in range(address_idx):
            line = lines[idx]
            # Check if this line contains species keywords
            if re.search(r'\b(Bass|Sunfish|Catfish|Crappie|Carp|Tilapia|Trout|Buffalo|Gar|Mullet|Eel|Oscar|Bowfin|Drum)\b', line, re.IGNORECASE):
                in_species = True
                species_lines.append(line)
            elif in_species:
                species_lines.append(line)
            else:
                name_lines.append(line)

        # Join lines
        name = ' '.join(name_lines).strip()
        species = ' '.join(species_lines).strip()
        address = lines[address_idx].strip() if address_idx < len(lines) else ""

        # If address doesn't have a comma, check if next line might be part of it
        if address and ',' not in address and address_idx + 1 < len(lines):
            address += ' ' + lines[address_idx + 1].strip()

        # Extract city from address (usually after comma)
        city_match = re.search(r',\s*([^,\d]+)$', address)
        city = city_match.group(1).strip() if city_match else "Houston"

        location = {
            'number': int(number),
            'name': name,
            'species': species,
            'address': address,
            'city': city
        }

        locations.append(location)

        print(f"[{number}] {name}")
        print(f"     Address: {address}")
        print(f"     Species: {species}")
        print()

    print(f"Total: Found {len(locations)} location entries")
    return locations


def main():
    pdf_path = "../../raw-data/houston_fishing.pdf"

    if not os.path.exists(pdf_path):
        print(f"[ERROR] PDF not found at: {pdf_path}")
        print("Download it first with curl or wget")
        return 1

    print("="*70)
    print("Parsing Houston Fishing Locations PDF")
    print("="*70)
    print()

    # Extract text from PDF
    print("[1/2] Extracting text from PDF...")
    text_pages = extract_text_from_pdf(pdf_path)
    print(f"[OK] Extracted text from {len(text_pages)} pages")
    print()

    # Save full text for debugging
    full_text = "\n".join(text_pages)
    with open("../../raw-data/houston_pdf_text.txt", 'w', encoding='utf-8') as f:
        f.write(full_text)
    print("[DEBUG] Saved full text to: ../../raw-data/houston_pdf_text.txt")

    # Parse locations
    print("[2/2] Parsing fishing locations...")
    locations = parse_fishing_locations(text_pages)

    if locations:
        output_path = "../../raw-data/houston_fishing_spots.json"
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(locations, f, indent=2)
        print(f"[OK] Saved {len(locations)} locations to: {output_path}")
    else:
        print("[WARN] No locations parsed - need to customize parser based on PDF structure")

    return 0


if __name__ == "__main__":
    sys.exit(main())
