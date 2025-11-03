"""
Import city fishing spots from manually extracted CSV
- Cross-reference with existing database entries using location verification
- Update addresses where needed
- Add species data to spot_votes table

Usage:
    python import_city_csv.py <csv_path> <city_name>

Example:
    python import_city_csv.py "../../raw-data/Houston PDF - Sheet1.csv" Houston
"""
import sys
sys.path.insert(0, '..')
import pandas as pd
import mysql.connector
from config import DB_CONFIG
from difflib import SequenceMatcher
import re
import requests
import time
from math import radians, cos, sin, asin, sqrt

# Species name mapping to database enum values
SPECIES_MAPPING = {
    'largemouth bass': 'largemouth_bass',
    'striped bass': 'striped_bass',
    'hybrid striped bass': 'striped_bass',
    'white bass': 'white_bass',
    'guadalupe bass': 'largemouth_bass',
    'smallmouth bass': 'largemouth_bass',
    'catfish': 'catfish',
    'channel catfish': 'catfish',
    'blue catfish': 'catfish',
    'sunfish': 'sunfish',
    'bluegill': 'sunfish',
    'redbreast sunfish': 'sunfish',
    'crappie': 'crappie',
    'white crappie': 'crappie',
    'carp': 'carp',
    'common carp': 'carp',
    'gar': 'gar',
    'buffalo': 'carp',
    'smallmouth buffalo': 'carp',
    'trout': 'trout',
    'rainbow trout': 'trout',
    'redfish': 'redfish',
    'flounder': 'flounder',
    'tilapia': 'sunfish',  # Close enough
    'mullet': 'carp',  # No exact match, using carp
    'oscar': 'sunfish',  # Exotic, but similar
}

def haversine_distance(lat1, lon1, lat2, lon2):
    """Calculate distance between two points in kilometers"""
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    r = 6371
    return c * r

def geocode_address(address, city='Houston'):
    """Forward geocode an address to lat/lon using Nominatim"""
    if not address or pd.isna(address):
        return None

    query = f"{address}, {city}, Texas"
    url = "https://nominatim.openstreetmap.org/search"

    params = {
        'q': query,
        'format': 'json',
        'limit': 1,
        'addressdetails': 1
    }

    headers = {
        'User-Agent': 'TexasFishingDirectory/1.0'
    }

    time.sleep(1.0)

    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        results = response.json()

        if results and len(results) > 0:
            lat = float(results[0]['lat'])
            lon = float(results[0]['lon'])
            return (lat, lon)
    except Exception as e:
        print(f"    [WARN] Geocoding failed: {e}")

    return None

def similarity(a, b):
    """Calculate similarity ratio between two strings"""
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

def normalize_name(name):
    """Normalize facility name for matching"""
    name = re.sub(r'\s*\(\d+\s*ponds?\)', '', name, flags=re.IGNORECASE)
    name = re.sub(r'\s+(park|reservoir|lake)$', '', name, flags=re.IGNORECASE)
    return name.strip().lower()

def parse_species(species_str):
    """Parse species string and map to database enum values"""
    if not species_str or pd.isna(species_str):
        return []

    # Remove asterisks (stocking indicators)
    species_str = species_str.replace('*', '')

    # Split by comma and normalize
    species_list = [s.strip().lower() for s in species_str.split(',')]

    # Map to database values
    db_species = []
    for species in species_list:
        for key, value in SPECIES_MAPPING.items():
            if key in species:
                if value not in db_species:
                    db_species.append(value)
                break

    return db_species

def find_matching_spot(facility_name, csv_address, cursor, city='Houston'):
    """Find matching spot with location verification"""
    normalized_facility = normalize_name(facility_name)

    # Geocode the CSV address
    csv_coords = None
    if csv_address and not pd.isna(csv_address):
        print(f"  Geocoding: {csv_address[:50]}...")
        csv_coords = geocode_address(csv_address, city)
        if csv_coords:
            print(f"    Coords: {csv_coords[0]:.4f}, {csv_coords[1]:.4f}")

    # Get all fishing spots
    cursor.execute("""
        SELECT id, name, water_body_name, address, latitude, longitude
        FROM fishing_spots
    """)

    spots = cursor.fetchall()
    best_match = None
    best_score = 0.0

    for spot in spots:
        spot_id, name, water_body, address, lat, lon = spot

        name_score = similarity(normalized_facility, normalize_name(name))
        water_score = 0.0
        if water_body:
            water_score = similarity(normalized_facility, normalize_name(water_body))

        score = max(name_score, water_score)

        if score > best_score:
            best_score = score
            best_match = {
                'id': spot_id,
                'name': name,
                'water_body': water_body,
                'address': address,
                'latitude': lat,
                'longitude': lon,
                'score': score,
                'distance_km': None
            }

    if best_score < 0.85:
        return None

    # Location verification
    if csv_coords and best_match:
        distance_km = haversine_distance(
            csv_coords[0], csv_coords[1],
            float(best_match['latitude']), float(best_match['longitude'])
        )
        best_match['distance_km'] = distance_km

        if distance_km > 5.0:
            print(f"    [WARN] Locations {distance_km:.1f}km apart - likely different places")
            return None
        else:
            print(f"    [OK] Distance: {distance_km:.2f}km")

    return best_match

def update_spot_with_address(spot_id, address, cursor, conn):
    """Update fishing spot with address"""
    if not address or pd.isna(address) or str(address).strip() == '':
        return False

    cursor.execute("""
        UPDATE fishing_spots
        SET address = %s
        WHERE id = %s AND (address IS NULL OR address = '')
    """, (address, spot_id))

    conn.commit()
    return cursor.rowcount > 0

def add_species_votes(spot_id, species_list, cursor, conn):
    """Add species to spot_votes table"""
    if not species_list:
        return 0

    added = 0
    for species in species_list:
        try:
            cursor.execute("""
                INSERT INTO spot_votes (fishing_spot_id, vote_type, vote_count)
                VALUES (%s, %s, 1)
                ON DUPLICATE KEY UPDATE vote_count = vote_count + 1
            """, (spot_id, species))
            added += 1
        except Exception as e:
            print(f"    [WARN] Could not add species {species}: {e}")

    conn.commit()
    return added

def parse_facility_name(facility_name):
    """
    Parse facility name to extract water body and park name if pattern is "Lake at Park"

    Returns:
        tuple: (display_name, water_body_name) or (facility_name, None) if no pattern match
    """
    # Check for pattern: "Water Body at Park Name"
    if ' at ' in facility_name:
        parts = facility_name.split(' at ', 1)
        water_body = parts[0].strip()
        park_name = parts[1].strip()

        # For matching purposes, we'll use the park name
        # For display, we'll keep the full name
        # For water_body field, we'll use the water body part
        return (park_name, water_body)

    return (facility_name, None)

def main():
    if len(sys.argv) < 2:
        print("Usage: python import_city_csv.py <csv_path> [city_name]")
        print('Example: python import_city_csv.py "../../raw-data/Houston PDF - Sheet1.csv" Houston')
        sys.exit(1)

    csv_path = sys.argv[1]
    city = sys.argv[2] if len(sys.argv) > 2 else 'Houston'

    # Load CSV
    df = pd.read_csv(csv_path)
    print(f"Loaded {len(df)} entries from {city} CSV\n")

    # Connect to database
    db_config = {k: v for k, v in DB_CONFIG.items() if k != 'cursorclass'}
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    matched = 0
    updated_addresses = 0
    added_species = 0
    not_matched = []

    for idx, row in df.iterrows():
        facility_name = row['Facility Name']
        species_str = row['Species Available']
        address = row['Facility Address'] if 'Facility Address' in row else None

        print(f"Processing: {facility_name}")

        # Parse facility name to separate water body from park name if needed
        search_name, water_body = parse_facility_name(facility_name)
        if water_body:
            print(f"  Parsed: Park='{search_name}', Water='{water_body}'")

        # Parse species
        species_list = parse_species(species_str)
        print(f"  Species: {', '.join(species_list) if species_list else 'None'}")

        # Find matching spot (use search_name for matching)
        match = find_matching_spot(search_name, address, cursor, city)

        if match:
            matched += 1
            print(f"  [MATCH] {match['name']} (score: {match['score']:.2f})")
            print(f"    DB ID: {match['id']}")

            # Update address if needed
            if address and not match['address']:
                if update_spot_with_address(match['id'], address, cursor, conn):
                    updated_addresses += 1
                    print(f"    [OK] Updated address")

            # Add species
            if species_list:
                count = add_species_votes(match['id'], species_list, cursor, conn)
                added_species += count
                print(f"    [OK] Added {count} species")
        else:
            not_matched.append({'name': facility_name, 'address': address})
            print(f"  [NO MATCH]")

        print()

    cursor.close()
    conn.close()

    print(f"\n{'='*60}")
    print(f"Summary - {city}:")
    print(f"  Total: {len(df)}")
    print(f"  Matched: {matched}")
    print(f"  Updated addresses: {updated_addresses}")
    print(f"  Species entries: {added_species}")
    print(f"  Not matched: {len(not_matched)}")

    if not_matched:
        print(f"\nNot matched (need to add as new entries):")
        for item in not_matched:
            print(f"  - {item['name']}")
            if item['address']:
                print(f"    Address: {item['address']}")

    print(f"{'='*60}")

if __name__ == '__main__':
    main()
