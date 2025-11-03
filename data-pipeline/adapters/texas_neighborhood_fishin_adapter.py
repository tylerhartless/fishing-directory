"""
Texas Neighborhood Fishin' Lakes Adapter

Imports TPWD Neighborhood Fishin' Lakes from GeoJSON data.
These are small urban ponds and lakes stocked by TPWD in partnership with local communities.

Data source: https://tpwd.texas.gov/fishboat/fish/programs/neighborhood-fishin/
"""

import pandas as pd
from typing import Optional
import sys
import os
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from etl_base import BaseDataAdapter, FishingSpotData


class TexasNeighborhoodFishinAdapter(BaseDataAdapter):
    """Adapter for Texas Neighborhood Fishin' Lakes from GeoJSON"""

    def __init__(self, enable_osm_enrichment=True):
        super().__init__(
            data_source_name="Texas_Neighborhood_Fishin",
            state_code="TX",
            enable_osm_enrichment=enable_osm_enrichment
        )

    def load_data(self, file_path: str) -> pd.DataFrame:
        """
        Load GeoJSON data and convert to DataFrame

        Args:
            file_path: Path to neighborhood_fishin_lakes.json
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
                'city': props['city'],
                'address': props.get('address', ''),
                'size': props.get('size', ''),
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
        city = row.get('city', '').replace('-', ' ')  # Fix "San-Antonio" -> "San Antonio"

        if not name:
            return None

        # Map cities to counties
        # (OSM enrichment doesn't update county, only water bodies/amenities)
        city_to_county = {
            'Amarillo': 'Potter',
            'Austin': 'Travis',
            'College Station': 'Brazos',
            'Hurst': 'Tarrant',
            'Fort Worth': 'Tarrant',
            'Duncanville': 'Dallas',
            'Mesquite City': 'Dallas',
            'Denton': 'Denton',
            'Pasadena': 'Harris',
            'Missouri City': 'Fort Bend',
            'Spring': 'Harris',
            'Katy': 'Harris',
            'San Angelo': 'Tom Green',
            'San Antonio': 'Bexar',
            'Waco': 'McLennan',
            'Wichita Falls': 'Wichita'
        }

        county = city_to_county.get(city, city)  # Fallback to city name if not in map

        # Get coordinates
        try:
            latitude = float(row['latitude'])
            longitude = float(row['longitude'])

            # Skip invalid coordinates
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

        # We'll let OSM enrichment find amenities
        amenities = {}

        # Build description
        size_text = f"{size} acres" if size else "small urban fishing pond"
        address = row.get('address', '')

        description = (
            f"{name} is a neighborhood fishing lake in {city} ({size_text}). "
            f"This lake is part of the Texas Neighborhood Fishin' Program, "
            f"providing convenient urban fishing access with regular stocking. "
        )

        if address:
            description += f"Located at {address}. "

        description += "Perfect for family fishing trips and teaching kids to fish."

        # For neighborhood lakes, the name is the water body
        # But OSM enrichment may find better names
        water_body = name

        return FishingSpotData(
            name=f"{name}",
            latitude=latitude,
            longitude=longitude,
            county=county,  # Will be enriched from coordinates
            water_body_name=water_body,
            spot_type='public_water',  # Neighborhood fishing areas
            description=description,
            state='TX',
            amenities=amenities,
            source_id=row.get('ID'),
            is_verified=True,
            meta_title=f"{name} - {city} Neighborhood Fishing Lake",
            meta_description=f"Fish at {name} in {city}. Urban fishing access with regular stocking through the Neighborhood Fishin' Program."
        )


def main():
    """Run the adapter"""
    from config import RAW_DATA_DIR
    import os

    json_path = os.path.join(RAW_DATA_DIR, 'neighborhood_fishin_lakes.json')

    if not os.path.exists(json_path):
        print(f"[ERROR] File not found: {json_path}")
        print("Run scripts/scrape_neighborhood_fishin.py first to generate the JSON file")
        return

    # Create adapter with OSM enrichment enabled
    adapter = TexasNeighborhoodFishinAdapter(enable_osm_enrichment=True)

    # Use base class process_and_import which includes deduplication
    rows_inserted = adapter.process_and_import(json_path)
    print(f"\n[SUCCESS] Complete! {rows_inserted} neighborhood fishing lakes imported.")


if __name__ == "__main__":
    main()
