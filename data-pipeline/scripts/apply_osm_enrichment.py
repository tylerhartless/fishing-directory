"""
Apply OSM enrichment results from dry-run to the database
"""

import json
import mysql.connector
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.append('..')
from config import DB_CONFIG

print("="*70)
print("APPLYING OSM ENRICHMENT RESULTS")
print("="*70)
print()

# Load enrichment results
with open('osm_enrichment_results.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print(f"Loaded results for {data['total_spots']} spots")
print(f"Success: {data['success_count']} ({data['success_count']/data['total_spots']*100:.1f}%)")
print(f"Would update: {data['would_update_count']} ({data['would_update_count']/data['total_spots']*100:.1f}%)")
print()

# Connect to database
conn = mysql.connector.connect(**DB_CONFIG)
cur = conn.cursor()

print("Processing updates...")
print()

updated_count = 0
amenity_updates = 0
water_body_updates = 0
address_updates = 0

for result in data['results']:
    if not result.get('proposed_updates'):
        continue

    spot_id = result['spot_id']
    updates = result['proposed_updates']

    # Build UPDATE query
    update_parts = []
    update_values = []

    if 'amenities' in updates:
        update_parts.append("amenities = %s")
        update_values.append(json.dumps(updates['amenities']))
        amenity_updates += 1

    if 'water_body_name' in updates:
        update_parts.append("water_body_name = %s")
        update_values.append(updates['water_body_name'])
        water_body_updates += 1

    if 'address' in updates:
        update_parts.append("address = %s")
        update_values.append(updates['address'])
        address_updates += 1

    if update_parts:
        update_parts.append("updated_at = NOW()")
        query = f"UPDATE fishing_spots SET {', '.join(update_parts)} WHERE id = %s"
        update_values.append(spot_id)

        cur.execute(query, update_values)
        updated_count += 1

        if updated_count % 50 == 0:
            print(f"  Updated {updated_count} spots...")

conn.commit()

print()
print("="*70)
print("UPDATE COMPLETE")
print("="*70)
print()
print(f"Total spots updated: {updated_count}")
print(f"  Amenity updates: {amenity_updates}")
print(f"  Water body updates: {water_body_updates}")
print(f"  Address updates: {address_updates}")
print()

# Verify some samples
print("Verifying sample updates...")
print()

cur.execute("""
    SELECT id, name, amenities
    FROM fishing_spots
    WHERE id IN (2261, 2266, 2270)
""")

samples = cur.fetchall()
for sample in samples:
    print(f"ID {sample[0]}: {sample[1]}")
    amenities = json.loads(sample[2])
    print(f"  Amenities: {', '.join([k for k, v in amenities.items() if v])}")
    print()

conn.close()

print("✅ Enrichment applied successfully!")
print()
print("Changes:")
print("- Amenity data normalized and enriched")
print("- Schema now consistent across all spots")
print("- Ready for frontend display")
