"""Show OSM enrichment results"""
import sys
import os
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from db_utils import get_connection

conn = get_connection(silent=True)
cursor = conn.cursor(dictionary=True)

print("="*70)
print("OSM Enrichment Results Summary")
print("="*70)
print()

# Overall stats
cursor.execute('SELECT COUNT(*) as total FROM fishing_spots WHERE spot_type="public_water"')
total = cursor.fetchone()['total']

cursor.execute('SELECT COUNT(*) as with_amenities FROM fishing_spots WHERE spot_type="public_water" AND amenities IS NOT NULL AND amenities != "{}"')
with_amenities = cursor.fetchone()['with_amenities']

print(f"Total public_water spots: {total}")
print(f"Spots with amenities: {with_amenities} ({100*with_amenities/total:.1f}%)")
print()

# Sample enriched spots
print("="*70)
print("Sample Spots with OSM-Enriched Amenities")
print("="*70)
cursor.execute('''
    SELECT name, water_body_name, county, amenities
    FROM fishing_spots
    WHERE spot_type = "public_water"
    AND amenities IS NOT NULL
    AND amenities != "{}"
    LIMIT 10
''')

for spot in cursor.fetchall():
    amenities = json.loads(spot['amenities'])
    amenity_list = [k for k, v in amenities.items() if v]
    print(f"{spot['name']:40} ({spot['county']} Co.)")
    print(f"  Water: {spot['water_body_name']}")
    if amenity_list:
        print(f"  Amenities: {', '.join(amenity_list)}")
    print()

# Water body examples
print("="*70)
print("Sample Water Body Names")
print("="*70)
cursor.execute('''
    SELECT name, water_body_name, county
    FROM fishing_spots
    WHERE spot_type = "public_water"
    LIMIT 10
''')

for spot in cursor.fetchall():
    print(f"{spot['name']:40} -> {spot['water_body_name']} ({spot['county']} Co.)")

cursor.close()
conn.close()

print()
print("="*70)
print("Enrichment Results Complete")
print("="*70)
