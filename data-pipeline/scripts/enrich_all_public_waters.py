"""
Enrich ALL public_water spots with OSM data
This will query OSM for addresses, amenities, and better names
"""
import requests
import time
import sys
import os
import json
from typing import Dict

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from db_utils import get_connection
from enrich_from_osm import OSMEnricher

def main():
    print("="*60)
    print("Full OSM Enrichment for Public Waters")
    print("="*60)
    print()

    # Connect to database
    conn = get_connection(silent=True)
    cursor = conn.cursor(dictionary=True)

    # Get all public_water spots
    cursor.execute("""
        SELECT id, name, water_body_name, county, latitude, longitude, address, amenities
        FROM fishing_spots
        WHERE spot_type = 'public_water'
        ORDER BY id
    """)
    spots = cursor.fetchall()

    print(f"Found {len(spots)} public_water spots to enrich")
    print(f"Estimated time: ~{int(len(spots) * 0.6 / 60)} minutes")
    print()

    enricher = OSMEnricher()

    success_count = 0
    error_count = 0
    updated_count = 0

    for i, spot in enumerate(spots, 1):
        print(f"[{i}/{len(spots)}] {spot['name']} ({spot['county']} County)", end='')

        # Query OSM for this spot
        osm_data = enricher.query_features_near_point(
            spot['latitude'],
            spot['longitude'],
            radius_meters=500
        )

        if not osm_data['success']:
            print(f" - ERROR: {osm_data.get('error')}")
            error_count += 1
            time.sleep(0.6)
            continue

        success_count += 1

        # Extract data
        water_bodies = osm_data['water_bodies']
        facilities = osm_data['facilities']
        amenities_found = osm_data['amenities']

        # Prepare updates
        updates = {}
        changes = []

        # Update water body if we found a better name
        if water_bodies and water_bodies[0]['distance_meters'] < 200:
            new_water_body = water_bodies[0]['name']
            if not spot['water_body_name'] or spot['water_body_name'] != new_water_body:
                updates['water_body_name'] = new_water_body
                changes.append(f"water_body={new_water_body}")

        # Update amenities if we found any
        if amenities_found:
            amenities_dict = {
                'parking': 'parking' in amenities_found,
                'restrooms': 'restrooms' in amenities_found,
                'picnic_area': 'picnic_area' in amenities_found,
                'boat_ramp': 'boat_ramp' in amenities_found,
                'fishing_pier': 'fishing_pier' in amenities_found,
            }

            # Only update if we don't have amenities or found new ones
            if not spot['amenities'] or amenities_found:
                updates['amenities'] = json.dumps(amenities_dict)
                changes.append(f"amenities={list(amenities_found)}")

        # Apply updates
        if updates:
            set_clauses = []
            values = []

            for field, value in updates.items():
                set_clauses.append(f"{field} = %s")
                values.append(value)

            values.append(spot['id'])

            update_query = f"UPDATE fishing_spots SET {', '.join(set_clauses)} WHERE id = %s"
            cursor.execute(update_query, tuple(values))
            conn.commit()

            updated_count += 1
            print(f" - UPDATED: {', '.join(changes)}")
        else:
            print(f" - OK (no changes)")

        # Rate limiting - OSM max 2 requests/second
        time.sleep(0.6)

        # Progress checkpoint every 100 spots
        if i % 100 == 0:
            print()
            print(f"--- Checkpoint: {i}/{len(spots)} processed ({updated_count} updated, {error_count} errors) ---")
            print()

    # Final summary
    print()
    print("="*60)
    print("Enrichment Complete!")
    print("="*60)
    print(f"Total spots processed: {len(spots)}")
    print(f"Successfully queried OSM: {success_count}")
    print(f"Updated with new data: {updated_count}")
    print(f"Errors: {error_count}")
    print("="*60)

    cursor.close()
    conn.close()

if __name__ == "__main__":
    main()
