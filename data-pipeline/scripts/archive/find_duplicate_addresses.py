"""
Find spots with duplicate addresses (same park/access point)
"""

import mysql.connector
import sys
import io

# Fix Windows console encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

sys.path.append('..')
from config import DB_CONFIG

def find_duplicates():
    conn = mysql.connector.connect(**DB_CONFIG)
    cur = conn.cursor(dictionary=True)

    # Find spots with duplicate addresses (same park/access point)
    print('=== Spots with Duplicate Addresses (Same Access Point) ===\n')

    cur.execute("""
        SELECT address, COUNT(*) as count
        FROM fishing_spots
        WHERE address IS NOT NULL
          AND address != ''
          AND spot_type IN ('public_water', 'state_park')
        GROUP BY address
        HAVING COUNT(*) > 1
        ORDER BY count DESC
        LIMIT 30
    """)

    address_groups = cur.fetchall()

    print(f'Found {len(address_groups)} addresses with multiple spots\n')
    print('='*80)

    for group in address_groups:
        address = group['address']
        count = group['count']

        print(f"\n📍 Address: {address}")
        print(f"   Count: {count} spots")
        print(f"   Spots:")

        # Get all spots with this address
        cur.execute("""
            SELECT id, name, spot_type, water_body_name, description
            FROM fishing_spots
            WHERE address = %s
            ORDER BY spot_type, name
        """, (address,))

        spots = cur.fetchall()

        for spot in spots:
            print(f"     - ID {spot['id']}: {spot['name']}")
            print(f"       Type: {spot['spot_type']}, Water: {spot['water_body_name']}")
            if len(spot['description']) > 100:
                print(f"       Desc: {spot['description'][:97]}...")
            else:
                print(f"       Desc: {spot['description']}")

        print()

    conn.close()

if __name__ == "__main__":
    find_duplicates()
