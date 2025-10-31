"""
California Department of Fish & Wildlife (CDFW) Data Adapter

Example adapter for California fishing access data.

Data Source: https://wildlife.ca.gov/Fishing/Ocean/Fishing-Map
Format: Example - adapt to actual CDFW data format
"""

import pandas as pd
from typing import Optional
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from etl_base import BaseDataAdapter, FishingSpotData


class CaliforniaDFWAdapter(BaseDataAdapter):
    """Adapter for California Department of Fish & Wildlife data"""

    def __init__(self):
        super().__init__(
            data_source_name="CDFW_Fishing_Access",
            state_code="CA"
        )

    def load_data(self, file_path: str) -> pd.DataFrame:
        """
        Load California DFW data

        Note: This is an example. Actual CDFW data format may vary.
        Could be CSV, JSON, or scraped from their website.
        """
        # Example: Could also handle JSON
        if file_path.endswith('.json'):
            return pd.read_json(file_path)
        else:
            return pd.read_csv(file_path)

    def transform_row(self, row: pd.Series, index: int) -> Optional[FishingSpotData]:
        """
        Transform California DFW row into standardized format

        Example mapping for hypothetical CDFW data structure:
        - 'Site_Name' -> name
        - 'Lat' -> latitude
        - 'Lon' -> longitude
        - 'County_Name' -> county
        - 'Water_Body' -> water_body_name
        - 'Access_Type' -> spot_type
        """

        # Example column mappings (adjust based on actual CDFW format)
        name = row.get('Site_Name') or row.get('name') or f"California Access Point {index}"

        try:
            # Handle different possible column names
            latitude = float(row.get('Lat') or row.get('latitude') or row.get('LATITUDE'))
            longitude = float(row.get('Lon') or row.get('longitude') or row.get('LONGITUDE'))
        except (ValueError, TypeError):
            print(f"      ⚠️  Skipping row {index}: Invalid coordinates")
            return None

        # Get county (California has 58 counties)
        county = row.get('County_Name') or row.get('county') or 'Unknown'

        # Get water body
        water_body = row.get('Water_Body') or row.get('waterbody') or 'Pacific Ocean'

        # Determine spot type
        access_type = str(row.get('Access_Type', 'unknown')).lower()
        if 'pier' in access_type or 'jetty' in access_type:
            spot_type = 'pier'
        elif 'ramp' in access_type or 'launch' in access_type:
            spot_type = 'boat_ramp'
        elif 'bank' in access_type or 'shore' in access_type:
            spot_type = 'bank_fishing'
        else:
            spot_type = 'bank_fishing'  # default

        # Create description
        description = f"Public fishing access at {water_body} in {county} County, California."

        # Add special notes for California
        if row.get('License_Free') == 'Yes':
            description += " Free Fishing Days - No license required on designated dates!"

        # Parse amenities
        amenities = {
            'parking': row.get('Has_Parking', 'No') == 'Yes',
            'restrooms': row.get('Has_Restrooms', 'No') == 'Yes',
            'pier': spot_type == 'pier',
            'boat_ramp': spot_type == 'boat_ramp',
            'disabled_access': row.get('ADA_Accessible', 'No') == 'Yes',
        }

        return FishingSpotData(
            name=name,
            latitude=latitude,
            longitude=longitude,
            county=county,
            water_body_name=water_body,
            spot_type=spot_type,
            description=description,
            state='CA',
            amenities=amenities,
            source_id=row.get('Site_ID') or row.get('id'),
            is_verified=True,
            meta_title=f"{name} - {county} County, California Fishing Access",
            meta_description=f"Public fishing access at {water_body}. GPS coordinates and amenities for {name}."
        )


def main():
    """Example usage"""
    import os
    from config import RAW_DATA_DIR

    adapter = CaliforniaDFWAdapter()

    # Try JSON or CSV
    csv_path = os.path.join(RAW_DATA_DIR, 'california_fishing_access.csv')
    json_path = os.path.join(RAW_DATA_DIR, 'california_fishing_access.json')

    file_path = csv_path if os.path.exists(csv_path) else json_path

    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        print(f"This is an example adapter. Adjust column mappings based on actual CDFW data format.")
        return

    rows_inserted = adapter.process_and_import(file_path)
    print(f"\n✅ California import complete! {rows_inserted} spots added.")


if __name__ == "__main__":
    main()
