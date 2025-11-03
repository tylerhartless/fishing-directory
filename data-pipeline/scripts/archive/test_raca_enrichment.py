"""Test OSM enrichment on RACA sites"""
import sys
import os
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from db_utils import get_connection
from enrich_from_osm import OSMEnricher

conn = get_connection(silent=True)
cursor = conn.cursor(dictionary=True)

# Get 5 sample RACA sites
cursor.execute('''
    SELECT id, name, latitude, longitude, water_body_name, amenities, county
    FROM fishing_spots
    WHERE spot_type = 'river_access'
    LIMIT 5
''')

sites = cursor.fetchall()

print('='*70)
print('OSM Enrichment Dry Run - RACA Sites (5 samples)')
print('='*70)
print()

enricher = OSMEnricher()

for site in sites:
    print(f"Testing: {site['name']}")
    print(f"  Current water body: {site['water_body_name']}")
    print(f"  Coordinates: {site['latitude']}, {site['longitude']}")

    # Enrich the site
    result = enricher.enrich_spot(site)

    if result['status'] != 'success':
        print(f"  [X] OSM query failed: {result.get('error', 'unknown error')}")
        print()
        continue

    # Check if water body was found
    if result.get('suggested_water_body'):
        if result['suggested_water_body'] != site['water_body_name']:
            print(f"  [+] OSM water body: {result['suggested_water_body']} (distance: {result['water_body_distance']:.0f}m)")
        else:
            print(f"  [=] OSM confirmed water body: {result['suggested_water_body']}")
    else:
        print(f"  [ ] No water body found in OSM")

    # Check facilities
    if result.get('facility_name'):
        print(f"  [+] Nearby facility: {result['facility_name']} (distance: {result['facility_distance']:.0f}m)")
        if result.get('facility_phone'):
            print(f"      Phone: {result['facility_phone']}")
        if result.get('facility_website'):
            print(f"      Website: {result['facility_website']}")
    else:
        print(f"  [ ] No facilities found")

    # Check amenities
    new_amenities = result.get('amenities', {})
    amenity_list = [k for k,v in new_amenities.items() if v]

    if amenity_list:
        print(f"  [+] OSM amenities: {', '.join(amenity_list)}")
    else:
        print(f"  [ ] No amenities found")

    print()

cursor.close()
conn.close()

print('='*70)
print('Dry run complete')
print('='*70)
