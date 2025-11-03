"""Check both American Legion Park Pond entries"""
import sys
sys.path.insert(0, '..')
import mysql.connector
from config import DB_CONFIG

db_config = {k: v for k, v in DB_CONFIG.items() if k != 'cursorclass'}
conn = mysql.connector.connect(**db_config)
cur = conn.cursor(dictionary=True)

print("Checking all American Legion Park Pond entries...\n")

# Find all American Legion entries
cur.execute("""
    SELECT id, name, slug, county, latitude, longitude, address,
           description, amenities, data_source, spot_type, water_body_name
    FROM fishing_spots
    WHERE name LIKE '%American Legion%'
    ORDER BY county, id
""")

entries = cur.fetchall()

print(f"Found {len(entries)} entries:\n")
print("="*80)

for i, spot in enumerate(entries, 1):
    print(f"\nEntry {i}:")
    print(f"  ID: {spot['id']}")
    print(f"  Name: {spot['name']}")
    print(f"  Slug: {spot['slug']}")
    print(f"  County: {spot['county']}")
    print(f"  Coords: {spot['latitude']}, {spot['longitude']}")
    print(f"  Address: {spot['address']}")
    print(f"  Description: {spot['description']}")
    print(f"  Amenities: {spot['amenities']}")
    print(f"  Data Source: {spot['data_source']}")
    print(f"  Spot Type: {spot['spot_type']}")
    print(f"  Water Body: {spot['water_body_name']}")

print("\n" + "="*80)

# Show which one is the Missouri City location
print("\nNOTE: The Missouri City location (4015 Lexington Blvd.) allows fishing.")
print("If there's a Harris County entry without confirmed fishing access, it should be removed.")

cur.close()
conn.close()
