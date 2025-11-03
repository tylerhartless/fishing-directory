"""
Analyze OSM enrichment dry-run results and compare to current database
"""

import json
import mysql.connector
import sys
import io
from collections import defaultdict

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.append('..')
from config import DB_CONFIG

# Load dry-run results
with open('osm_enrichment_results.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print("="*70)
print("OSM ENRICHMENT DRY-RUN ANALYSIS")
print("="*70)
print()

# Overall statistics
print(f"Total spots processed: {data['total_spots']}")
print(f"Successful enrichment: {data['success_count']} ({data['success_count']/data['total_spots']*100:.1f}%)")
print(f"Errors encountered: {data['error_count']} ({data['error_count']/data['total_spots']*100:.1f}%)")
print(f"Would update: {data['would_update_count']} ({data['would_update_count']/data['total_spots']*100:.1f}%)")
print()

# Analyze what types of updates would happen
amenity_additions = defaultdict(int)
address_updates = 0
water_body_updates = 0

for result in data['results']:
    if result.get('proposed_updates'):
        updates = result['proposed_updates']

        if 'address' in updates:
            address_updates += 1

        if 'water_body_name' in updates:
            water_body_updates += 1

        if 'amenities' in updates:
            # Parse amenities to see what's being added
            try:
                current = json.loads(result.get('current_amenities', '{}'))
                proposed = updates['amenities']

                for key, value in proposed.items():
                    if value and not current.get(key):
                        amenity_additions[key] += 1
            except:
                pass

print("="*70)
print("UPDATE BREAKDOWN")
print("="*70)
print(f"\nAddress updates: {address_updates}")
print(f"Water body name updates: {water_body_updates}")
print(f"\nAmenities being added:")
for amenity, count in sorted(amenity_additions.items(), key=lambda x: x[1], reverse=True):
    print(f"  {amenity}: {count} spots")

print()
print("="*70)
print("SAMPLE UPDATES (First 15 with changes)")
print("="*70)
print()

count = 0
for result in data['results']:
    if result.get('proposed_updates') and count < 15:
        print(f"ID {result['spot_id']}: {result['name']} ({result['county']} County)")

        updates = result['proposed_updates']

        if 'address' in updates:
            print(f"  📍 Address: {result['current_address']} → {updates['address']}")

        if 'water_body_name' in updates:
            print(f"  🌊 Water body: {result['current_water_body']} → {updates['water_body_name']}")

        if 'amenities' in updates:
            current = json.loads(result.get('current_amenities', '{}'))
            proposed = updates['amenities']

            new_amenities = []
            for key, value in proposed.items():
                if value and not current.get(key):
                    new_amenities.append(key)

            if new_amenities:
                print(f"  ✨ New amenities: {', '.join(new_amenities)}")

        print()
        count += 1

print()
print("="*70)
print("QUALITY CHECK - Potential Issues")
print("="*70)
print()

# Check for spots where OSM found NO data nearby
no_osm_data = 0
for result in data['results']:
    if (not result.get('osm_water_bodies') and
        not result.get('osm_facilities') and
        not result.get('osm_amenities')):
        no_osm_data += 1

print(f"Spots with NO OSM data nearby: {no_osm_data}")

# Check error types
print(f"\nErrors by type:")
errors = [r for r in data['results'] if r.get('error')]
for err in errors[:5]:
    print(f"  ID {err['spot_id']}: {err.get('error', 'Unknown error')}")

print()
print("="*70)
print("RECOMMENDATION")
print("="*70)
print()

success_rate = data['success_count'] / data['total_spots'] * 100
update_rate = data['would_update_count'] / data['total_spots'] * 100

if success_rate > 95 and update_rate > 50:
    print("✅ RECOMMEND APPLYING UPDATES")
    print(f"   - High success rate ({success_rate:.1f}%)")
    print(f"   - Good coverage ({update_rate:.1f}% would get new data)")
    print(f"   - {amenity_additions.get('parking', 0)} spots getting parking info")
    print(f"   - {amenity_additions.get('restrooms', 0)} spots getting restroom info")
    print(f"   - {amenity_additions.get('picnic_area', 0)} spots getting picnic area info")
    print(f"   - {address_updates} spots getting addresses")
elif success_rate > 90:
    print("⚠️  CAUTIOUSLY RECOMMEND")
    print(f"   - Decent success rate ({success_rate:.1f}%)")
    print(f"   - Review errors before applying")
else:
    print("❌ DO NOT RECOMMEND")
    print(f"   - Too many errors ({data['error_count']} errors)")

print()
