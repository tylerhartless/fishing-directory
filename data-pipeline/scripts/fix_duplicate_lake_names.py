"""
Fix spot names with duplicate "Lake" (e.g., "Lake Lady Bird Lake" -> "Lady Bird Lake")
"""

import mysql.connector
import sys
import io

# Fix Windows console encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

sys.path.append('..')
from config import DB_CONFIG

def fix_duplicate_lake_names():
    conn = mysql.connector.connect(**DB_CONFIG)
    cur = conn.cursor(dictionary=True)

    print("=== Fixing Duplicate 'Lake' in Spot Names ===\n")

    # Manual mapping of correct names
    fixes = {
        3268: "Oakland Lake Park (Lake Fosdic)",  # Keep park name, show lake in parens
        3045: "Big Creek Lake",
        3203: "Bois d'Arc Lake",
        3048: "Bonham State Park Lake",
        3066: "Cleburne State Park Lake",
        2810: "Lake Dabney (Houston Wilderness Park)",  # Lake Dabney is the primary name
        3113: "Lady Bird Lake",
        3115: "Lake Corpus Christi",
        3116: "Lake Fork",
        3118: "Lake O' the Pines",
        3135: "Meridian State Park Lake",
        3137: "Mill Creek Lake",
        3142: "Mountain Creek Lake",
        3163: "Purtis Creek State Park Lake",
        3195: "White Rock Lake",
        2980: "Lakewood Lake",  # This is correct - Lakewood is the name
    }

    cur.execute("""
        SELECT id, name, spot_type, county
        FROM fishing_spots
        WHERE name LIKE '%Lake%Lake%'
        ORDER BY name
    """)
    spots = cur.fetchall()

    print(f"Found {len(spots)} spots with duplicate 'Lake'\n")

    for spot in spots:
        spot_id = spot['id']
        old_name = spot['name']

        if spot_id in fixes:
            new_name = fixes[spot_id]
            print(f"ID {spot_id}: {spot['spot_type']}, {spot['county']} County")
            print(f"  Before: {old_name}")
            print(f"  After:  {new_name}")

            cur.execute("""
                UPDATE fishing_spots
                SET name = %s
                WHERE id = %s
            """, (new_name, spot_id))

            print("  ✓ Fixed\n")
        else:
            print(f"⚠️  ID {spot_id}: {old_name} - NO FIX DEFINED")
            print(f"   (Please manually check this one)\n")

    conn.commit()

    print(f"\n{'='*60}")
    print(f"✓ Fixed {len([s for s in spots if s['id'] in fixes])} spot names")

    conn.close()

if __name__ == "__main__":
    fix_duplicate_lake_names()
