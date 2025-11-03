"""
DRY RUN: Enrich ALL public_water spots with OSM data
This will query OSM and save results to JSON for review before applying to DB
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
    print("DRY RUN: OSM Enrichment for Public Waters")
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
    print(f"Estimated time: ~{int(len(spots) * 2.0 / 60)} minutes (with 2-second delay + retries)")
    print(f"Results will be saved to: osm_enrichment_results.json")
    print()

    enricher = OSMEnricher()

    results = []
    success_count = 0
    error_count = 0
    would_update_count = 0

    for i, spot in enumerate(spots, 1):
        print(f"[{i}/{len(spots)}] {spot['name']} ({spot['county']} County)", end='', flush=True)

        # Query OSM for this spot with retry logic
        max_retries = 3
        retry_count = 0
        osm_data = None

        while retry_count < max_retries:
            osm_data = enricher.query_features_near_point(
                spot['latitude'],
                spot['longitude'],
                radius_meters=500
            )

            # If successful or non-retryable error, break
            if osm_data['success']:
                break

            # Check if it's a rate limit error (429)
            error_msg = osm_data.get('error', '')
            if '429' in str(error_msg) and retry_count < max_retries - 1:
                retry_count += 1
                print(f" - Rate limited, retry {retry_count}/{max_retries-1}...", end='', flush=True)
                time.sleep(5)  # Wait 5 seconds before retry
            else:
                break

        result = {
            'spot_id': spot['id'],
            'name': spot['name'],
            'county': spot['county'],
            'current_water_body': spot['water_body_name'],
            'current_address': spot['address'],
            'current_amenities': spot['amenities']
        }

        if not osm_data['success']:
            result['status'] = 'error'
            result['error'] = osm_data.get('error')
            print(f" - ERROR: {result['error']}")
            error_count += 1
            results.append(result)
            time.sleep(2.0)  # Increased delay
            continue

        success_count += 1

        # Extract data
        water_bodies = osm_data['water_bodies']
        facilities = osm_data['facilities']
        amenities_found = osm_data['amenities']

        result['status'] = 'success'
        result['osm_water_bodies'] = water_bodies
        result['osm_facilities'] = facilities
        result['osm_amenities'] = list(amenities_found)

        # Determine what would be updated
        proposed_updates = {}

        # Water body
        if water_bodies and water_bodies[0]['distance_meters'] < 200:
            new_water_body = water_bodies[0]['name']
            if not spot['water_body_name'] or spot['water_body_name'] != new_water_body:
                proposed_updates['water_body_name'] = new_water_body
                proposed_updates['water_body_distance'] = water_bodies[0]['distance_meters']

        # Amenities
        if amenities_found:
            amenities_dict = {
                'parking': 'parking' in amenities_found,
                'restrooms': 'restrooms' in amenities_found,
                'picnic_area': 'picnic_area' in amenities_found,
                'boat_ramp': 'boat_ramp' in amenities_found,
                'fishing_pier': 'fishing_pier' in amenities_found,
            }
            if not spot['amenities'] or amenities_found:
                proposed_updates['amenities'] = amenities_dict

        result['proposed_updates'] = proposed_updates

        if proposed_updates:
            would_update_count += 1
            print(f" - WOULD UPDATE: {list(proposed_updates.keys())}")
        else:
            print(f" - OK (no changes)")

        results.append(result)

        # Rate limiting - 2 second delay between requests
        time.sleep(2.0)

        # Progress checkpoint every 100 spots
        if i % 100 == 0:
            print()
            print(f"--- Checkpoint: {i}/{len(spots)} processed ({would_update_count} would update, {error_count} errors) ---")
            print()

    # Save results to JSON
    output_file = 'osm_enrichment_results.json'
    with open(output_file, 'w') as f:
        json.dump({
            'total_spots': len(spots),
            'success_count': success_count,
            'error_count': error_count,
            'would_update_count': would_update_count,
            'results': results
        }, f, indent=2)

    # Final summary
    print()
    print("="*60)
    print("DRY RUN Complete!")
    print("="*60)
    print(f"Total spots processed: {len(spots)}")
    print(f"Successfully queried OSM: {success_count}")
    print(f"Would update with new data: {would_update_count}")
    print(f"Errors: {error_count}")
    print(f"\nResults saved to: {output_file}")
    print("="*60)

    cursor.close()
    conn.close()

if __name__ == "__main__":
    main()
