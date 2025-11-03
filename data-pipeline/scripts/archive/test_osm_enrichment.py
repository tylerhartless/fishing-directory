"""
Test OSM enrichment integration in ETL pipeline

This script tests importing a small batch of community lakes with OSM enrichment enabled.
"""

import sys
import os
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from adapters.texas_community_lakes_adapter import TexasCommunityLakesAdapter
from config import RAW_DATA_DIR

def main():
    print("="*60)
    print("Testing OSM Enrichment in ETL Pipeline")
    print("="*60)
    print()

    # Load original data
    json_path = os.path.join(RAW_DATA_DIR, 'community_fishing_lakes.json')

    with open(json_path, 'r') as f:
        data = json.load(f)

    # Create a test subset - Montgomery County spots
    test_features = [f for f in data['features'] if f['properties'].get('county') == 'Montgomery'][:3]

    test_data = {
        'type': 'FeatureCollection',
        'features': test_features
    }

    # Save test data
    test_path = os.path.join(RAW_DATA_DIR, 'test_community_lakes.json')
    with open(test_path, 'w') as f:
        json.dump(test_data, f, indent=2)

    print(f"Created test dataset with {len(test_features)} Montgomery County spots")
    print()

    # Run adapter with OSM enrichment enabled
    adapter = TexasCommunityLakesAdapter(enable_osm_enrichment=True)
    rows_inserted = adapter.process_and_import(test_path)

    print(f"\n[SUCCESS] Test complete! {rows_inserted} spots processed with OSM enrichment")

    # Clean up test file
    os.remove(test_path)


if __name__ == "__main__":
    main()
