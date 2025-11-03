"""
Fix fishing spots that should be associated with state parks or nature centers
"""

import mysql.connector
import sys
import io

# Fix Windows console encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

sys.path.append('..')
from config import DB_CONFIG

def fix_spots():
    conn = mysql.connector.connect(**DB_CONFIG)
    cur = conn.cursor(dictionary=True)

    changes = []

    # 1. Fix 75-Acre Lake - should be part of Choke Canyon State Park Calliham Unit
    print("=== Fixing 75-Acre Lake ===")
    cur.execute("""
        SELECT id, name, spot_type, latitude, longitude
        FROM fishing_spots
        WHERE id = 2798
    """)
    spot = cur.fetchone()

    if spot:
        print(f"Current: ID {spot['id']}, Name: {spot['name']}, Type: {spot['spot_type']}")
        print("Action: Delete - this is a duplicate of the Calliham Unit state park")
        print("Reason: 75-Acre Lake is the pond inside Choke Canyon State Park Calliham Unit")

        cur.execute("DELETE FROM fishing_spots WHERE id = 2798")
        changes.append(f"Deleted ID 2798 (75-Acre Lake duplicate)")
        print("✓ Deleted\n")

    # 2. Fix Salad Bowl Pond - should note it's in Jesse H Jones Nature Center
    print("=== Fixing Salad Bowl Pond ===")
    cur.execute("""
        SELECT id, name, spot_type, description
        FROM fishing_spots
        WHERE id = 2647
    """)
    spot = cur.fetchone()

    if spot:
        print(f"Current: ID {spot['id']}, Name: {spot['name']}")
        print(f"Current description: {spot['description']}")

        new_desc = "Community fishing lake inside Jesse H Jones Nature Center in Humble. Regularly stocked by TPWD."

        cur.execute("""
            UPDATE fishing_spots
            SET description = %s
            WHERE id = 2647
        """, (new_desc,))

        changes.append(f"Updated ID 2647 (Salad Bowl Pond) description to mention Jesse H Jones Nature Center")
        print(f"New description: {new_desc}")
        print("✓ Updated\n")

    # 3. Fix Jones Youth Fishing Lake - should note it's in Jesse H Jones Nature Center
    print("=== Fixing Jones Youth Fishing Lake ===")
    cur.execute("""
        SELECT id, name, spot_type, description
        FROM fishing_spots
        WHERE id = 2641
    """)
    spot = cur.fetchone()

    if spot:
        print(f"Current: ID {spot['id']}, Name: {spot['name']}")
        print(f"Current description: {spot['description']}")

        new_desc = "Youth fishing lake inside Jesse H Jones Nature Center in Humble. Regularly stocked by TPWD."

        cur.execute("""
            UPDATE fishing_spots
            SET description = %s
            WHERE id = 2641
        """, (new_desc,))

        changes.append(f"Updated ID 2641 (Jones Youth Fishing Lake) description to mention Jesse H Jones Nature Center")
        print(f"New description: {new_desc}")
        print("✓ Updated\n")

    # 4. Fix Dennis Johnston Park Pond duplicate
    print("=== Fixing Dennis Johnston Park Pond Duplicate ===")
    cur.execute("""
        SELECT id, name, spot_type, latitude, longitude, amenities, data_source
        FROM fishing_spots
        WHERE name LIKE '%Dennis Johnston%'
        ORDER BY id
    """)
    duplicates = cur.fetchall()

    if len(duplicates) == 2:
        print(f"Found {len(duplicates)} Dennis Johnston Park Pond entries:")
        for dup in duplicates:
            print(f"  ID {dup['id']}: Source={dup['data_source']}, Coords=({dup['latitude']}, {dup['longitude']})")
            print(f"    Amenities: {dup['amenities']}")

        # Keep the one with more amenities (ID 2627 from Community Lakes)
        # Delete the City PDF one (ID 3240) which has fewer amenities
        print("\nAction: Keep ID 2627 (more amenities), delete ID 3240")

        cur.execute("DELETE FROM fishing_spots WHERE id = 3240")
        changes.append(f"Deleted ID 3240 (Dennis Johnston Park Pond duplicate with fewer amenities)")
        print("✓ Deleted duplicate\n")

    # Commit all changes
    conn.commit()

    print("\n" + "="*60)
    print("Summary of changes:")
    for i, change in enumerate(changes, 1):
        print(f"{i}. {change}")

    print(f"\nTotal changes: {len(changes)}")

    conn.close()

if __name__ == "__main__":
    fix_spots()
