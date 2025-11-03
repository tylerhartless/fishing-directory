"""
Remove exact duplicate spots with the same address
Keep the one with the most complete data (from Community Lakes source preferred)
"""

import mysql.connector
import sys
import io

# Fix Windows console encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

sys.path.append('..')
from config import DB_CONFIG

def remove_duplicates():
    conn = mysql.connector.connect(**DB_CONFIG)
    cur = conn.cursor(dictionary=True)

    # IDs to delete (City PDF duplicates - keeping Community Lakes versions)
    duplicates_to_delete = [
        3252,  # Resoft Park Lake (keep 2315)
        3242,  # Eldridge Park Pond (keep 2554)
        3248,  # Kitty Hollow Lake (keep 2559)
        3253,  # Seabourne Creek Park (keep 2565)
        3236,  # Burke-Crenshaw Lake (keep 2622)
        3239,  # Challenger 7 Pond (keep 2624)
        3241,  # Eisenhower Park Pond (keep 2629)
        3250,  # Mary Jo Peckham Park (keep 2642)
        3238,  # Carl Barton Jr. Park Pond (keep 2805)
        3265,  # City Lake Park - Mesquite (keep 3020)
    ]

    print("=== Removing Duplicate Address Spots ===\n")

    for spot_id in duplicates_to_delete:
        # Get spot info before deleting
        cur.execute("SELECT id, name, address, data_source FROM fishing_spots WHERE id = %s", (spot_id,))
        spot = cur.fetchone()

        if spot:
            print(f"Deleting ID {spot['id']}: {spot['name']}")
            print(f"  Address: {spot['address']}")
            print(f"  Source: {spot['data_source']}")

            cur.execute("DELETE FROM fishing_spots WHERE id = %s", (spot_id,))
            print("  ✓ Deleted\n")

    # Handle the Espada/South Side Lions case separately
    print("=== Fixing Espada/South Side Lions Bad Address ===")
    cur.execute("""
        SELECT id, name, address, latitude, longitude
        FROM fishing_spots
        WHERE id IN (3274, 3275)
        ORDER BY id
    """)
    espada_spots = cur.fetchall()

    for spot in espada_spots:
        print(f"ID {spot['id']}: {spot['name']}")
        print(f"  Current address: {spot['address']}")
        print(f"  Action: Delete (bad address, needs geocoding)")
        cur.execute("DELETE FROM fishing_spots WHERE id = %s", (spot['id'],))
        print("  ✓ Deleted\n")

    conn.commit()

    print(f"\n{'='*60}")
    print(f"Total duplicates removed: {len(duplicates_to_delete) + 2}")
    print("\nNote: Espada Park Lake and South Side Lions Park Pond need to be")
    print("re-added with proper addresses and coordinates from San Antonio data.")

    conn.close()

if __name__ == "__main__":
    remove_duplicates()
