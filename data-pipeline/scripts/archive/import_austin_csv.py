"""
Import Austin fishing spots from manually extracted CSV
- Cross-reference with existing database entries
- Update addresses where needed
- Add species data to spot_votes table
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
    'guadalupe bass': 'largemouth_bass',  # Similar enough to largemouth
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
    'buffalo': 'carp',  # Close enough
    'smallmouth buffalo': 'carp',
    'trout': 'trout',
    'redfish': 'redfish',
    'flounder': 'flounder'
}

def haversine_distance(lat1, lon1, lat2, lon2):
    """
    Calculate the great circle distance between two points
    on the earth (specified in decimal degrees)
    Returns distance in kilometers
    """
    # Convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    # Haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    r = 6371  # Radius of earth in kilometers
    return c * r

def geocode_address(address, city='Austin'):
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

    # Rate limit: 1 request/second
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
    # Remove common suffixes
    name = re.sub(r'\s*\(\d+\s*ponds?\)', '', name, flags=re.IGNORECASE)
    name = re.sub(r'\s+(park|reservoir|lake)$', '', name, flags=re.IGNORECASE)
    return name.strip().lower()

def parse_species(species_str):
    """Parse species string and map to database enum values"""
    if not species_str or pd.isna(species_str):
        return []

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

def find_matching_spot(facility_name, csv_address, cursor):
    """
    Find matching fishing spot in database using fuzzy matching + location verification

    Args:
        facility_name: Name of facility from CSV
        csv_address: Address from CSV (for geocoding verification)
        cursor: Database cursor

    Returns:
        Match dict with location verification or None
    """
    normalized_facility = normalize_name(facility_name)

    # Geocode the CSV address to get coordinates for verification
    csv_coords = None
    if csv_address and not pd.isna(csv_address):
        print(f"  Geocoding CSV address: {csv_address[:50]}...")
        csv_coords = geocode_address(csv_address)
        if csv_coords:
            print(f"    Got coords: {csv_coords[0]:.4f}, {csv_coords[1]:.4f}")

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

        # Check name similarity
        name_score = similarity(normalized_facility, normalize_name(name))

        # Check water body similarity (for lakes)
        water_score = 0.0
        if water_body:
            water_score = similarity(normalized_facility, normalize_name(water_body))

        # Use the best score
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

    # Only return if confidence is high enough
    # Using 0.85 threshold to avoid false matches
    if best_score < 0.85:
        return None

    # LOCATION VERIFICATION: If we have coordinates from CSV, verify proximity
    if csv_coords and best_match:
        distance_km = haversine_distance(
            csv_coords[0], csv_coords[1],
            float(best_match['latitude']), float(best_match['longitude'])
        )
        best_match['distance_km'] = distance_km

        # If distance is > 5km, this is likely a false match (same name, different place)
        if distance_km > 5.0:
            print(f"    [WARN] Name matches but locations are {distance_km:.1f}km apart - likely different places")
            return None
        else:
            print(f"    [OK] Distance verification: {distance_km:.2f}km apart")

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
            # Use INSERT ... ON DUPLICATE KEY UPDATE to handle existing entries
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

def main():
    # Load CSV
    csv_path = '../../raw-data/Austin PDF - Sheet1.csv'
    df = pd.read_csv(csv_path)

    print(f"Loaded {len(df)} entries from Austin CSV\n")
    print(f"Columns: {list(df.columns)}\n")

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

        # Parse species
        species_list = parse_species(species_str)
        print(f"  Species: {', '.join(species_list) if species_list else 'None'}")

        # Find matching spot (with location verification)
        match = find_matching_spot(facility_name, address, cursor)

        if match:
            matched += 1
            print(f"  [MATCH] Found: {match['name']} (score: {match['score']:.2f})")
            print(f"    DB ID: {match['id']}")
            print(f"    Current address: {match['address']}")

            # Update address if CSV has one and DB doesn't
            if address and not match['address']:
                if update_spot_with_address(match['id'], address, cursor, conn):
                    updated_addresses += 1
                    print(f"    [OK] Updated address: {address}")

            # Add species
            if species_list:
                count = add_species_votes(match['id'], species_list, cursor, conn)
                added_species += count
                print(f"    [OK] Added {count} species")
        else:
            not_matched.append(facility_name)
            print(f"  [NO MATCH] Could not find in database")

        print()

    cursor.close()
    conn.close()

    print(f"\n{'='*60}")
    print(f"Summary:")
    print(f"  Total entries: {len(df)}")
    print(f"  Matched: {matched}")
    print(f"  Updated addresses: {updated_addresses}")
    print(f"  Species entries added: {added_species}")
    print(f"  Not matched: {len(not_matched)}")

    if not_matched:
        print(f"\nNot matched entries:")
        for name in not_matched:
            print(f"  - {name}")

    print(f"{'='*60}")

if __name__ == '__main__':
    main()
