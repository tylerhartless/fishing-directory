"""
Fix county issues and reorganize nature center fishing spots
"""

import mysql.connector
import sys
import io
from geopy.geocoders import Nominatim

# Fix Windows console encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

sys.path.append('..')
from config import DB_CONFIG

def get_county_from_coords(lat, lon):
    """Reverse geocode coordinates to get county"""
    try:
        geolocator = Nominatim(user_agent="fishing_directory")
        location = geolocator.reverse(f"{lat}, {lon}", exactly_one=True)

        if location and location.raw.get('address'):
            address = location.raw['address']
            county = address.get('county', '').replace(' County', '')
            if county:
                return county
        return None
    except Exception as e:
        print(f"  Geocoding error: {e}")
        return None

def fix_issues():
    conn = mysql.connector.connect(**DB_CONFIG)
    cur = conn.cursor(dictionary=True)

    changes = []

    # 1. Fix Brazos River Nature Center county
    print("=== Fixing Brazos River Nature Center County ===")
    cur.execute("""
        UPDATE fishing_spots
        SET county = 'Mclennan'
        WHERE id = 3208
    """)
    changes.append("Fixed Brazos River Nature Center county: 'northern McLennan' → 'Mclennan'")
    print("✓ Fixed county to 'Mclennan'\n")

    # 2. Fix River Access spots with Unknown county
    print("=== Fixing River Access Spots with Unknown County ===")
    cur.execute("""
        SELECT id, name, latitude, longitude, address
        FROM fishing_spots
        WHERE spot_type = 'river_access' AND county = 'Unknown'
        ORDER BY id
    """)
    unknown_county_spots = cur.fetchall()

    for spot in unknown_county_spots:
        print(f"ID {spot['id']}: {spot['name']}")

        # Check if address already contains county info
        if spot['address'] and 'County' in spot['address']:
            # Extract county from address
            import re
            match = re.search(r'(\w+)\s+County', spot['address'])
            if match:
                county = match.group(1)
                cur.execute("""
                    UPDATE fishing_spots
                    SET county = %s
                    WHERE id = %s
                """, (county, spot['id']))
                changes.append(f"ID {spot['id']}: Set county to '{county}' from address")
                print(f"  → Set county to '{county}' from address")
                continue

        # Try reverse geocoding
        print(f"  Geocoding {spot['latitude']}, {spot['longitude']}...")
        county = get_county_from_coords(spot['latitude'], spot['longitude'])

        if county:
            cur.execute("""
                UPDATE fishing_spots
                SET county = %s
                WHERE id = %s
            """, (county, spot['id']))
            changes.append(f"ID {spot['id']}: Set county to '{county}' via geocoding")
            print(f"  → Set county to '{county}'")
        else:
            print(f"  → Could not determine county")

        print()

    # 3. Reorganize Jesse H Jones Nature Center
    print("=== Reorganizing Jesse H Jones Nature Center ===")

    # Check if we need to create the nature center entry
    cur.execute("""
        SELECT id FROM fishing_spots
        WHERE name = 'Jesse H. Jones Park and Nature Center'
    """)
    nature_center = cur.fetchone()

    if not nature_center:
        print("Creating Jesse H. Jones Park and Nature Center entry...")

        # Use coordinates from Salad Bowl Pond (center of the park)
        cur.execute("""
            INSERT INTO fishing_spots
            (name, slug, spot_type, county, state, latitude, longitude,
             water_body_name, description, data_source, created_at, updated_at)
            VALUES (
                'Jesse H. Jones Park and Nature Center',
                'jesse-h-jones-park-and-nature-center-harris',
                'public_water',
                'Harris',
                'TX',
                30.0249000,
                -95.2869000,
                'Spring Creek',
                'Nature park with multiple fishing ponds including Salad Bowl Pond and Jones Youth Fishing Lake. Regularly stocked by TPWD.',
                'Manual_Consolidation',
                NOW(),
                NOW()
            )
        """)
        changes.append("Created Jesse H. Jones Park and Nature Center main entry")
        print("✓ Created main nature center entry")

        # Update Salad Bowl Pond to reference the nature center
        cur.execute("""
            UPDATE fishing_spots
            SET description = 'Fishing pond inside Jesse H. Jones Park and Nature Center. Regularly stocked by TPWD.'
            WHERE id = 2647
        """)

        # Update Jones Youth Fishing Lake
        cur.execute("""
            UPDATE fishing_spots
            SET description = 'Youth fishing lake inside Jesse H. Jones Park and Nature Center. Regularly stocked by TPWD.'
            WHERE id = 2641
        """)

        changes.append("Updated Salad Bowl Pond and Jones Youth Lake descriptions to reference main park")
        print("✓ Updated pond descriptions to reference main park\n")
    else:
        print("Nature center entry already exists\n")

    # Commit all changes
    conn.commit()

    print("\n" + "="*60)
    print("Summary of changes:")
    for i, change in enumerate(changes, 1):
        print(f"{i}. {change}")

    print(f"\nTotal changes: {len(changes)}")

    conn.close()

if __name__ == "__main__":
    fix_issues()
