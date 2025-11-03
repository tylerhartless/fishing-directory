"""
Generate summary report from OSM enrichment results

Shows what was enriched and provides examples of improvements made
"""

import sys
import os
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from db_utils import get_connection


def generate_summary():
    """Generate enrichment summary report"""

    # Check if progress file exists
    progress_file = 'osm_enrichment_progress.json'
    if not os.path.exists(progress_file):
        print("[WARN] No progress file found - enrichment may not have run yet")
        return

    # Load progress data
    with open(progress_file, 'r') as f:
        progress = json.load(f)

    stats = progress.get('stats', {})
    processed_count = len(progress.get('processed_ids', []))
    last_update = progress.get('last_update', 'Unknown')

    print("="*70)
    print("OSM Enrichment Summary Report")
    print("="*70)
    print()
    print(f"Last Update: {last_update}")
    print()
    print("Statistics:")
    print(f"  Total spots:           {stats.get('total', 0):5}")
    print(f"  Processed:             {processed_count:5} ({100*processed_count/max(stats.get('total', 1), 1):.1f}%)")
    print(f"  Successfully enriched: {stats.get('enriched', 0):5} ({100*stats.get('enriched', 0)/max(processed_count, 1):.1f}%)")
    print(f"  Water bodies found:    {stats.get('water_bodies_found', 0):5}")
    print(f"  Facilities found:      {stats.get('facilities_found', 0):5}")
    print(f"  Amenities added:       {stats.get('amenities_added', 0):5}")
    print(f"  Errors:                {stats.get('errors', 0):5} ({100*stats.get('errors', 0)/max(processed_count, 1):.1f}%)")
    print(f"  Skipped:               {stats.get('skipped', 0):5}")
    print()

    # Query database for some examples
    conn = get_connection(silent=True)
    cursor = conn.cursor(dictionary=True)

    # Find spots with enriched water body names
    print("="*70)
    print("Sample Water Body Names Found by OSM")
    print("="*70)
    cursor.execute("""
        SELECT name, water_body_name, county
        FROM fishing_spots
        WHERE spot_type = 'public_water'
        AND water_body_name NOT LIKE '%Park%'
        AND water_body_name NOT LIKE 'Park Waters'
        LIMIT 10
    """)
    water_bodies = cursor.fetchall()

    for wb in water_bodies:
        print(f"  {wb['name']:40} -> {wb['water_body_name']} ({wb['county']} Co.)")

    # Find spots with amenities
    print()
    print("="*70)
    print("Sample Spots with OSM-Enriched Amenities")
    print("="*70)
    cursor.execute("""
        SELECT name, county, amenities
        FROM fishing_spots
        WHERE spot_type = 'public_water'
        AND amenities IS NOT NULL
        AND amenities != '{}'
        LIMIT 10
    """)
    amenity_spots = cursor.fetchall()

    for spot in amenity_spots:
        amenities = json.loads(spot['amenities'])
        amenity_list = [k for k, v in amenities.items() if v]
        print(f"  {spot['name']:40} ({spot['county']} Co.)")
        print(f"    Amenities: {', '.join(amenity_list)}")

    # Find spots with facility info in description
    print()
    print("="*70)
    print("Sample Spots with Facility Context")
    print("="*70)
    cursor.execute("""
        SELECT name, county, description
        FROM fishing_spots
        WHERE spot_type = 'public_water'
        AND description LIKE '%Located at%'
        LIMIT 5
    """)
    facility_spots = cursor.fetchall()

    for spot in facility_spots:
        # Extract facility name from description
        desc = spot['description']
        if 'Located at ' in desc:
            facility_part = desc.split('Located at ')[1].split('.')[0]
            print(f"  {spot['name']:40} ({spot['county']} Co.)")
            print(f"    Located at: {facility_part}")

    cursor.close()
    conn.close()

    print()
    print("="*70)
    print("Report Complete")
    print("="*70)


if __name__ == "__main__":
    generate_summary()
