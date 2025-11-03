"""
Texas Community Fishing Lakes Adapter

Imports TPWD Community Fishing Lakes from GeoJSON data.
These are smaller lakes and ponds stocked by TPWD for public fishing access.

Data source: https://tpwd.texas.gov/fishboat/fish/recreational/lakes/cfl.phtml
"""

import pandas as pd
from typing import Optional
import sys
import os
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from etl_base import BaseDataAdapter, FishingSpotData


class TexasCommunityLakesAdapter(BaseDataAdapter):
    """Adapter for Texas Community Fishing Lakes from GeoJSON"""

    def __init__(self, enable_osm_enrichment=True):
        super().__init__(
            data_source_name="Texas_Community_Lakes",
            state_code="TX",
            enable_osm_enrichment=enable_osm_enrichment
        )

    def load_data(self, file_path: str) -> pd.DataFrame:
        """
        Load GeoJSON data and convert to DataFrame

        Args:
            file_path: Path to community_fishing_lakes.json
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            geojson = json.load(f)

        print(f"Loaded GeoJSON with {len(geojson['features'])} features")

        # Convert GeoJSON features to flat records
        records = []
        for feature in geojson['features']:
            props = feature['properties']
            coords = feature['geometry']['coordinates']

            record = {
                'ID': props['ID'],
                'name': props['name'],
                'county': props['county'],
                'size': props['size'],
                'longitude': coords[0],
                'latitude': coords[1]
            }
            records.append(record)

        df = pd.DataFrame(records)
        print(f"Converted to {len(df)} records")

        return df

    def transform_row(self, row: pd.Series, index: int) -> Optional[FishingSpotData]:
        """Transform lake row into standardized format"""

        name = row.get('name')
        county = row.get('county')

        if not name or not county:
            return None

        # Get coordinates
        try:
            latitude = float(row['latitude'])
            longitude = float(row['longitude'])

            # Skip invalid coordinates (some entries have [0,0])
            if latitude == 0 and longitude == 0:
                print(f"      [WARN] Skipping {name}: Invalid coordinates (0,0)")
                return None

            # Sanity check for Texas bounds
            if not (25 < latitude < 37) or not (-107 < longitude < -93):
                print(f"      [WARN] Skipping {name}: Coordinates outside Texas bounds")
                return None

        except (ValueError, TypeError) as e:
            print(f"      [WARN] Skipping {name}: Cannot parse coordinates - {e}")
            return None

        # Get size
        try:
            size = float(row.get('size', 0))
        except:
            size = None

        # Don't infer amenities from names - use OSM enrichment instead
        # Default to empty amenities dict
        amenities = {}

        # Build description
        size_text = f"{size} acres" if size else "small lake"
        description = (
            f"{name} is a community fishing lake in {county} County ({size_text}). "
            f"This lake is part of the Texas Community Fishing Lake Program, "
            f"which stocks fish regularly and provides public fishing access with no license required for those under 17 or using a pole and line only. "
            f"Perfect for family fishing trips and beginners."
        )

        # Determine water body name
        # For community lakes, the name IS the water body
        water_body = name

        return FishingSpotData(
            name=f"{name}",
            latitude=latitude,
            longitude=longitude,
            county=county,
            water_body_name=water_body,
            spot_type='public_water',  # Public lakes, ponds, neighborhood fishing areas
            description=description,
            state='TX',
            amenities=amenities,
            source_id=row.get('ID'),
            is_verified=True,
            meta_title=f"{name} - {county} County Public Fishing Lake",
            meta_description=f"Fish at {name}, a public fishing lake in {county} County. Regularly stocked, free access for youth anglers."
        )


def main():
    """Run the adapter"""
    from config import RAW_DATA_DIR
    import os

    json_path = os.path.join(RAW_DATA_DIR, 'community_fishing_lakes.json')

    if not os.path.exists(json_path):
        print(f"[ERROR] File not found: {json_path}")
        print("Run scripts/convert_cfl_to_json.py first to generate the JSON file")
        return

    # Create adapter
    adapter = TexasCommunityLakesAdapter()

    # Use base class process_and_import which includes deduplication
    rows_inserted = adapter.process_and_import(json_path)
    print(f"\n[SUCCESS] Complete! {rows_inserted} community lakes imported.")


if __name__ == "__main__":
    main()
