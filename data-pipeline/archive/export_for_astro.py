"""
Export fishing spots data to JSON for Astro static generation

This script exports all fishing spots from MySQL to a JSON file
that Astro can use during static site generation.

Run this script whenever you update the database to regenerate the static site.
"""

import json
from db_utils import execute_query
from config import PROCESSED_DATA_DIR
import os

def export_fishing_spots():
    """Export all fishing spots to JSON"""

    print("Fetching fishing spots from database...")

    query = """
        SELECT
            id,
            name,
            slug,
            latitude,
            longitude,
            county,
            water_body_name,
            spot_type,
            description,
            amenities,
            data_source,
            is_verified,
            is_active,
            meta_title,
            meta_description,
            created_at,
            updated_at
        FROM fishing_spots
        WHERE is_active = TRUE
        ORDER BY county, name
    """

    spots = execute_query(query, fetch=True)

    # Convert amenities from JSON string to object
    for spot in spots:
        if spot['amenities']:
            spot['amenities'] = json.loads(spot['amenities'])

        # Convert datetime to ISO string
        if spot['created_at']:
            spot['created_at'] = spot['created_at'].isoformat()
        if spot['updated_at']:
            spot['updated_at'] = spot['updated_at'].isoformat()

    # Save to frontend public data folder
    output_file = '../frontend/public/data/fishing-spots.json'
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(spots, f, indent=2, ensure_ascii=False)

    print(f"\n{'='*50}")
    print(f"SUCCESS: Exported {len(spots)} fishing spots")
    print(f"Output: {output_file}")
    print(f"{'='*50}")

    # Also create a summary by county
    counties = {}
    for spot in spots:
        county = spot['county']
        if county not in counties:
            counties[county] = {
                'name': county,
                'spot_count': 0,
                'spot_types': {}
            }

        counties[county]['spot_count'] += 1

        spot_type = spot['spot_type']
        if spot_type not in counties[county]['spot_types']:
            counties[county]['spot_types'][spot_type] = 0
        counties[county]['spot_types'][spot_type] += 1

    # Save county summary
    summary_file = '../frontend/public/data/counties.json'
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(list(counties.values()), f, indent=2)

    print(f"\nAlso created: {summary_file}")
    print(f"Total counties: {len(counties)}")

if __name__ == "__main__":
    print("="*50)
    print("Export Fishing Spots for Astro")
    print("="*50)

    export_fishing_spots()

    print("\nNext steps:")
    print("1. cd ../frontend")
    print("2. npm run build")
    print("3. Deploy to production")
