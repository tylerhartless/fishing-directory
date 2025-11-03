"""Find and report all duplicate spots (same name + county)"""
import sys
sys.path.insert(0, '..')
import mysql.connector
from config import DB_CONFIG

db_config = {k: v for k, v in DB_CONFIG.items() if k != 'cursorclass'}
conn = mysql.connector.connect(**db_config)
cur = conn.cursor(dictionary=True)

print("Scanning for duplicate spots (same name + county)...\n")

# Find all name+county combinations with more than 1 entry
cur.execute("""
    SELECT name, county, COUNT(*) as count
    FROM fishing_spots
    WHERE county IS NOT NULL
    GROUP BY name, county
    HAVING count > 1
    ORDER BY count DESC, name ASC
""")

duplicates = cur.fetchall()

if not duplicates:
    print("No duplicates found!")
else:
    print(f"Found {len(duplicates)} sets of duplicates:\n")
    print("="*80)

    for i, dup in enumerate(duplicates, 1):
        print(f"\n{i}. {dup['name']} in {dup['county']} County ({dup['count']} entries)")
        print("-" * 80)

        # Get details of all entries for this name+county
        cur.execute("""
            SELECT id, slug, latitude, longitude, address, description,
                   amenities, data_source, spot_type
            FROM fishing_spots
            WHERE name = %s AND county = %s
            ORDER BY id ASC
        """, (dup['name'], dup['county']))

        entries = cur.fetchall()

        for entry in entries:
            print(f"  Entry ID {entry['id']}:")
            print(f"    Slug: {entry['slug']}")
            print(f"    Coords: {entry['latitude']}, {entry['longitude']}")
            print(f"    Address: {entry['address']}")
            print(f"    Description: {entry['description'][:80] if entry['description'] else 'None'}...")
            print(f"    Amenities: {'Yes' if entry['amenities'] else 'None'}")
            print(f"    Data Source: {entry['data_source']}")
            print(f"    Spot Type: {entry['spot_type']}")
            print()

    print("\n" + "="*80)
    print(f"Total: {len(duplicates)} sets of duplicates found")
    print("="*80)

cur.close()
conn.close()
