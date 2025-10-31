"""
Generic CSV Adapter

Use this adapter for simple CSV files with standard column names.
You can configure column mappings without writing custom code.

Example CSV columns:
- name, latitude, longitude, county, water_body, description, state
- Or: spot_name, lat, lon, county_name, lake, notes, state_code

Just provide a column mapping configuration!
"""

import pandas as pd
from typing import Optional, Dict
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from etl_base import BaseDataAdapter, FishingSpotData


class GenericCSVAdapter(BaseDataAdapter):
    """
    Generic adapter for CSV files with configurable column mappings

    Usage:
        column_map = {
            'name': 'Site_Name',
            'latitude': 'Lat',
            'longitude': 'Lon',
            'county': 'County_Name',
            'water_body': 'Lake',
            'state': 'State'
        }

        adapter = GenericCSVAdapter(
            data_source_name="My_Data_Source",
            state_code="NY",
            column_mapping=column_map
        )
    """

    def __init__(self, data_source_name: str, state_code: str, column_mapping: Dict[str, str]):
        """
        Initialize generic adapter with column mappings

        Args:
            data_source_name: Name for this data source
            state_code: Two-letter state code
            column_mapping: Dictionary mapping our fields to CSV columns
                Required keys: name, latitude, longitude, county, water_body
                Optional keys: description, spot_type, amenities, address, zip_code
        """
        super().__init__(data_source_name, state_code)
        self.column_mapping = column_mapping

        # Validate required fields
        required = ['name', 'latitude', 'longitude', 'county', 'water_body']
        missing = [key for key in required if key not in column_mapping]
        if missing:
            raise ValueError(f"Missing required column mappings: {missing}")

    def load_data(self, file_path: str) -> pd.DataFrame:
        """Load CSV data"""
        return pd.read_csv(file_path)

    def get_mapped_value(self, row: pd.Series, our_field: str, default=None):
        """Get value from row using column mapping"""
        csv_column = self.column_mapping.get(our_field)
        if csv_column:
            return row.get(csv_column, default)
        return default

    def transform_row(self, row: pd.Series, index: int) -> Optional[FishingSpotData]:
        """Transform generic CSV row into standardized format"""

        name = self.get_mapped_value(row, 'name')
        if not name:
            print(f"      ⚠️  Skipping row {index}: Missing name")
            return None

        try:
            latitude = float(self.get_mapped_value(row, 'latitude', 0))
            longitude = float(self.get_mapped_value(row, 'longitude', 0))

            if latitude == 0 or longitude == 0:
                return None
        except (ValueError, TypeError):
            return None

        county = self.get_mapped_value(row, 'county', 'Unknown')
        water_body = self.get_mapped_value(row, 'water_body', 'Local Waters')

        # Optional fields
        description = self.get_mapped_value(row, 'description') or \
                     f"Public fishing access at {water_body} in {county} County."

        spot_type = self.get_mapped_value(row, 'spot_type', 'bank_fishing').lower()

        # Normalize spot_type
        if spot_type not in ['boat_ramp', 'pier', 'bank_fishing', 'state_park']:
            if 'ramp' in spot_type or 'launch' in spot_type:
                spot_type = 'boat_ramp'
            elif 'pier' in spot_type or 'dock' in spot_type:
                spot_type = 'pier'
            elif 'park' in spot_type:
                spot_type = 'state_park'
            else:
                spot_type = 'bank_fishing'

        # Try to parse amenities if provided as JSON string
        amenities_raw = self.get_mapped_value(row, 'amenities')
        amenities = None
        if amenities_raw:
            import json
            try:
                amenities = json.loads(amenities_raw) if isinstance(amenities_raw, str) else amenities_raw
            except:
                pass  # If amenities parsing fails, leave as None

        return FishingSpotData(
            name=name,
            latitude=latitude,
            longitude=longitude,
            county=county,
            water_body_name=water_body,
            spot_type=spot_type,
            description=description,
            state=self.state_code,
            amenities=amenities,
            source_id=self.get_mapped_value(row, 'source_id') or self.get_mapped_value(row, 'id'),
            is_verified=True,
            address=self.get_mapped_value(row, 'address'),
            zip_code=self.get_mapped_value(row, 'zip_code'),
            meta_title=f"{name} - {county} County, {self.state_code}",
            meta_description=f"Public fishing access at {water_body}. GPS coordinates and information."
        )


def main():
    """Example usage with custom column mapping"""
    import os
    from config import RAW_DATA_DIR

    # Example: New York State fishing access data
    # Their CSV has columns: Site_Name, Lat, Lon, County_Name, Waterbody, Access_Type

    column_map = {
        'name': 'Site_Name',
        'latitude': 'Lat',
        'longitude': 'Lon',
        'county': 'County_Name',
        'water_body': 'Waterbody',
        'spot_type': 'Access_Type',
        'description': 'Notes'
    }

    adapter = GenericCSVAdapter(
        data_source_name="NYS_DEC_Fishing_Access",
        state_code="NY",
        column_mapping=column_map
    )

    csv_path = os.path.join(RAW_DATA_DIR, 'new_york_fishing.csv')

    if not os.path.exists(csv_path):
        print(f"❌ File not found: {csv_path}")
        print("\nTo use this adapter:")
        print("1. Get a CSV file with fishing spot data")
        print("2. Create a column mapping dictionary")
        print("3. Pass it to GenericCSVAdapter")
        print("\nNo custom Python code needed!")
        return

    rows_inserted = adapter.process_and_import(csv_path)
    print(f"\n✅ Import complete! {rows_inserted} spots added.")


if __name__ == "__main__":
    main()
