"""
Add unmatched entries from all 4 city CSVs as new fishing spots
"""
import sys
sys.path.insert(0, '..')
import pandas as pd
import mysql.connector
from config import DB_CONFIG
import requests
import time
from slugify import slugify

# Species mapping (same as import script)
SPECIES_MAPPING = {
    'largemouth bass': 'largemouth_bass',
    'striped bass': 'striped_bass',
    'hybrid striped bass': 'striped_bass',
    'white bass': 'white_bass',
    'guadalupe bass': 'largemouth_bass',
    'smallmouth bass': 'largemouth_bass',
    'spotted bass': 'largemouth_bass',
    'yellow bass': 'white_bass',
    'catfish': 'catfish',
    'channel catfish': 'catfish',
    'blue catfish': 'catfish',
    'sunfish': 'sunfish',
    'bluegill': 'sunfish',
    'redbreast sunfish': 'sunfish',
    'redear sunfish': 'sunfish',
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
    'red drum': 'redfish',
    'flounder': 'flounder',
    'tilapia': 'sunfish',
    'mullet': 'carp',
    'oscar': 'sunfish',
}

def geocode_address(address, city):
    """Forward geocode an address"""
    query = f"{address}, {city}, Texas"
    url = "https://nominatim.openstreetmap.org/search"

    params = {
        'q': query,
        'format': 'json',
        'limit': 1,
        'addressdetails': 1
    }

    headers = {'User-Agent': 'TexasFishingDirectory/1.0'}
    time.sleep(1.0)

    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        results = response.json()

        if results and len(results) > 0:
            lat = float(results[0]['lat'])
            lon = float(results[0]['lon'])
            county = results[0].get('address', {}).get('county', '').replace(' County', '')
            return (lat, lon, county)
    except Exception as e:
        print(f"    [WARN] Geocoding failed: {e}")

    return None

def parse_species(species_str):
    """Parse species string"""
    if not species_str or pd.isna(species_str):
        return []

    species_str = species_str.replace('*', '')
    species_list = [s.strip().lower() for s in species_str.split(',')]

    db_species = []
    for species in species_list:
        for key, value in SPECIES_MAPPING.items():
            if key in species:
                if value not in db_species:
                    db_species.append(value)
                break

    return db_species

def parse_facility_name(facility_name):
    """Parse 'Lake at Park' patterns"""
    if ' at ' in facility_name:
        parts = facility_name.split(' at ', 1)
        water_body = parts[0].strip()
        park_name = parts[1].strip()
        return (facility_name, park_name, water_body)
    return (facility_name, None, None)

# List of unmatched entries from all cities
UNMATCHED_ENTRIES = [
    # Austin
    {"name": "Bright Lake at Old Settlers Park", "species": "Largemouth Bass, Sunfish", "address": "3300 East Palm Valley Boulevard, Round Rock", "city": "Austin"},
    {"name": "Colorado River at Little Webberville", "species": "Largemouth Bass, Guadalupe Bass, Sunfish", "address": "910 Water Street, Manor", "city": "Austin"},
    {"name": "Colorado River at Big Webberville", "species": "Largemouth Bass, Guadalupe Bass, Sunfish", "address": "2305 Park Lane, Webberville", "city": "Austin"},
    {"name": "Colorado River at Fisherman's Park", "species": "Largemouth Bass, Guadalupe Bass, Sunfish", "address": "1200 Willow Street, Bastrop", "city": "Austin"},
    {"name": "Colorado River at Colorado River Wildlife Sanctuary", "species": "Largemouth Bass, Guadalupe Bass, Sunfish", "address": "5827 Levander Loop, Austin", "city": "Austin"},
    {"name": "Travis County East Metropolitan Park (3 ponds)", "species": "Sunfish, Largemouth Bass", "address": "18706 Blake Manor Circle, Manor", "city": "Austin"},
    {"name": "Bradfield Village Park (2 ponds)", "species": "Sunfish, Largemouth Bass", "address": "Crescent Drive, Buda", "city": "Austin"},
    {"name": "Lake Pflugerville", "species": "Largemouth Bass, Sunfish", "address": "18216 Weiss Lane, Pflugerville", "city": "Austin"},
    {"name": "Barkley Meadows Park (2 ponds)", "species": "Largemouth Bass, Sunfish", "address": "4529 S SH 130 SVRD NB, Del Valle", "city": "Austin"},
    {"name": "McKinney Falls State Park", "species": "Sunfish, Largemouth Bass", "address": "5808 McKinney Falls Pkwy, Austin", "city": "Austin"},

    # Houston
    {"name": "American Legion Park Pond", "species": "Largemouth Bass, Sunfish, Catfish, Rainbow Trout, Carp, Tilapia", "address": "4015 Lexington Blvd., Missouri City", "city": "Houston"},
    {"name": "Community Park Lake", "species": "Largemouth Bass, Sunfish, Catfish, Crappie, Rainbow Trout, Carp, Gar", "address": "1700 Glenn Lakes Ln., Missouri City", "city": "Houston"},
    {"name": "Cypress Creek Park at Timberlane", "species": "Largemouth Bass, Sunfish, Catfish, Crappie, Rainbow Trout, Gar", "address": "2114 Naplechase Crest Dr., Spring", "city": "Houston"},
    {"name": "Cypress Park Lake", "species": "Largemouth Bass, Sunfish, Catfish, Crappie, Carp, Gar", "address": "12925 N Eldridge Pkwy., Cypress", "city": "Houston"},
    {"name": "Hackberry Park", "species": "Sunfish", "address": "7777 S Dairy Ashford Rd., Houston", "city": "Houston"},
    {"name": "Herman Little Pond", "species": "Largemouth Bass, Sunfish, Catfish, Rainbow Trout", "address": "18660 Casper Dr., Spring", "city": "Houston"},

    # San Antonio
    {"name": "Espada Park Lake", "species": "Guadalupe Bass, Channel Catfish, Largemouth Bass", "address": "1750 SE Military Drive, San Antonio", "city": "San Antonio"},
    {"name": "South Side Lions Park Pond", "species": "Channel Catfish", "address": "4600 Pecan Valley Drive, San Antonio", "city": "San Antonio"},
    {"name": "Victor Braunig Lake", "species": "Red Drum, Channel Catfish, Largemouth Bass", "address": "17500 Donop Road, San Antonio", "city": "San Antonio"},
    {"name": "Live Oak City Lake at Main City Park", "species": "Channel Catfish, Largemouth Bass, Sunfish", "address": "18001 Park Drive, Live Oak", "city": "San Antonio"},
    {"name": "St. Mary's Elmendorf Lake Park", "species": "Channel Catfish", "address": "3700 W Commerce Street, San Antonio", "city": "San Antonio"},
    {"name": "Woodlawn Lake Park", "species": "Channel Catfish", "address": "1103 Cincinnati Avenue, San Antonio", "city": "San Antonio"},
    {"name": "Patrolman John Randolph Wheeler Park", "species": "Channel Catfish", "address": "10239 Ingram Road, San Antonio", "city": "San Antonio"},
    {"name": "Earl Scott Pond, in the Leon Creek Greenway", "species": "Channel Catfish, Largemouth Bass, Sunfish", "address": "13101 Babcock Road, San Antonio", "city": "San Antonio"},
    {"name": "Fischer Park", "species": "Largemouth Bass, Sunfish", "address": "1935 Hill Top Summit Road, New Braunfels", "city": "San Antonio"},

    # DFW
    {"name": "Lake Como", "species": "Largemouth Bass, Sunfish", "address": "3401 Lake Como Dr., Fort Worth", "city": "DFW"},
    {"name": "River Park", "species": "Largemouth Bass, Sunfish, Carp, Rainbow Trout", "address": "3100 Bryant Irvin Rd., Fort Worth", "city": "DFW"},
    {"name": "Sonora Park", "species": "Largemouth Bass, Sunfish", "address": "263 New Hope Rd., Kennedale", "city": "DFW"},
    {"name": "Generations Park at Boys Ranch", "species": "Largemouth Bass, Sunfish", "address": "2801 Forest Ridge Dr., Bedford", "city": "DFW"},
    {"name": "Mike Lewis Park", "species": "Sunfish, Rainbow Trout", "address": "2410 N Carrier Pkwy., Grand Prairie", "city": "DFW"},
    {"name": "Bachman Lake", "species": "Largemouth Bass, Crappie", "address": "3500 W. Northwest Hwy., Dallas", "city": "DFW"},
    {"name": "Bob Jones Park", "species": "Largemouth Bass, Sunfish", "address": "3901 N White Chapel Blvd., Southlake", "city": "DFW"},
    {"name": "Fosdic Lake at Oakland Lake Park", "species": "Largemouth Bass, Sunfish", "address": "1645 Lake Shore Dr., Fort Worth", "city": "DFW"},
    {"name": "Josey Ranch Park", "species": "Largemouth Bass, Sunfish, Carp", "address": "1440 Keller Springs Rd., Carrollton", "city": "DFW"},
    {"name": "Randol Mill Duck Pond", "species": "Largemouth Bass, Sunfish, Rainbow Trout", "address": "1901 W. Randol Mill Rd., Arlington", "city": "DFW"},
    {"name": "Town Hall Lake", "species": "Largemouth Bass, Sunfish, Catfish", "address": "1100 Bear Creek Pkwy., Keller", "city": "DFW"},
    {"name": "Russell Creek Park", "species": "Largemouth Bass, Sunfish, Catfish", "address": "3500 McDermott Rd., Plano", "city": "DFW"},
    {"name": "Frontier Park", "species": "Largemouth Bass, Sunfish, Rainbow Trout", "address": "1551 Frontier Pkwy., Prosper", "city": "DFW"},
]

def main():
    db_config = {k: v for k, v in DB_CONFIG.items() if k != 'cursorclass'}
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    added_count = 0
    failed_count = 0

    print(f"Adding {len(UNMATCHED_ENTRIES)} new fishing spots...\n")

    for entry in UNMATCHED_ENTRIES:
        name = entry['name']
        species_str = entry['species']
        address = entry['address']
        city = entry['city']

        print(f"Adding: {name}")

        # Parse facility name for "at" pattern
        display_name, park_name, water_body = parse_facility_name(name)

        if water_body:
            print(f"  Parsed: '{park_name}' with water body '{water_body}'")
            # Use park name for the spot name
            spot_name = park_name
            water_body_name = water_body
        else:
            spot_name = name
            water_body_name = None

        # Geocode address
        print(f"  Geocoding: {address}...")
        geocode_result = geocode_address(address, city)

        if not geocode_result:
            print(f"  [ERROR] Could not geocode address")
            failed_count += 1
            continue

        lat, lon, county = geocode_result
        print(f"    Coords: {lat:.4f}, {lon:.4f}")
        print(f"    County: {county}")

        # Create slug
        slug = slugify(spot_name)

        # Check if slug exists
        cursor.execute("SELECT id FROM fishing_spots WHERE slug = %s", (slug,))
        if cursor.fetchone():
            # Add county to make unique
            slug = slugify(f"{spot_name}-{county}")
            print(f"    Slug collision, using: {slug}")

        # Parse species
        species_list = parse_species(species_str)
        print(f"  Species: {', '.join(species_list)}")

        # Insert fishing spot
        try:
            cursor.execute("""
                INSERT INTO fishing_spots (
                    name, slug, latitude, longitude, county, water_body_name,
                    spot_type, address, data_source, state, is_verified
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                spot_name,
                slug,
                lat,
                lon,
                county,
                water_body_name,
                'public_water',  # City PDF spots are public waters
                address,
                f'Texas_City_PDFs_{city}',
                'TX',
                False
            ))

            spot_id = cursor.lastrowid

            # Add species votes
            for species in species_list:
                try:
                    cursor.execute("""
                        INSERT INTO spot_votes (fishing_spot_id, vote_type, vote_count)
                        VALUES (%s, %s, 1)
                    """, (spot_id, species))
                except:
                    pass

            conn.commit()
            added_count += 1
            print(f"  [OK] Added with ID {spot_id}\n")

        except Exception as e:
            print(f"  [ERROR] Failed to add: {e}\n")
            failed_count += 1
            conn.rollback()

    cursor.close()
    conn.close()

    print(f"\n{'='*60}")
    print(f"Summary:")
    print(f"  Total entries: {len(UNMATCHED_ENTRIES)}")
    print(f"  Successfully added: {added_count}")
    print(f"  Failed: {failed_count}")
    print(f"{'='*60}")

if __name__ == '__main__':
    main()
