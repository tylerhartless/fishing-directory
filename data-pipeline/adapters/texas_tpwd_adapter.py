"""
Texas Parks & Wildlife Department (TPWD) Data Adapter

Handles TPWD boat ramp CSV data with specific column mappings.

Data Source: https://tpwd.texas.gov/gis/resources/boat-access.phtml
Format: CSV with columns like TPWAID, Latitude, Longitude, AccessTypeDescription
"""

import pandas as pd
import re
from typing import Optional
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from etl_base import BaseDataAdapter, FishingSpotData


class TexasTPWDAdapter(BaseDataAdapter):
    """Adapter for Texas Parks & Wildlife Department boat ramp data"""

    def __init__(self):
        super().__init__(
            data_source_name="TPWD_Boat_Ramps",
            state_code="TX"
        )

    def load_data(self, file_path: str) -> pd.DataFrame:
        """Load TPWD CSV data"""
        return pd.read_csv(file_path, encoding='utf-8')

    def transform_row(self, row: pd.Series, index: int) -> Optional[FishingSpotData]:
        """Transform TPWD row into standardized format"""

        # Extract TPWAID (unique identifier)
        tpwaid = str(row.get('TPWAID', f'unknown{index}'))

        # Parse county from TPWAID (e.g., 'anderson001' -> 'Anderson')
        county_match = re.match(r'([a-zA-Z]+)', tpwaid)
        county = county_match.group(1).title() if county_match else 'Unknown'

        # Get water body name - handle bad data
        water_body_raw = str(row.get('AccessTypeDescription', 'Local Waters')).strip()

        # Get access type for description
        access_type = row.get('AccessType', 'River/Stream')

        # Check if AccessTypeDescription is empty or looks like facility info
        # Bad patterns: empty, whitespace, "boat ramp", "day use", "fishing pier", etc.
        facility_keywords = ['boat ramp', 'day use', 'fishing pier', 'habitat', 'parking']
        is_empty = not water_body_raw or water_body_raw == ''
        is_facility_desc = any(keyword in water_body_raw.lower() for keyword in facility_keywords)

        # Use generic name if AccessTypeDescription is empty or contains facility info
        if is_empty or is_facility_desc:
            if 'Lake' in access_type or 'Reservoir' in access_type:
                water_body = f"{county} County Lake"
            elif 'River' in access_type or 'Stream' in access_type:
                water_body = f"{county} County Waterway"
            elif 'Bay' in access_type or 'Beach' in access_type:
                water_body = f"{county} County Coastal Access"
            else:
                water_body = f"{county} County Public Waters"
        else:
            water_body = water_body_raw

        # Validate coordinates
        try:
            latitude = float(row.get('Latitude', 0))
            longitude = float(row.get('Longitude', 0))

            if latitude == 0 or longitude == 0:
                print(f"      ⚠️  Skipping row {index}: Invalid coordinates")
                return None
        except (ValueError, TypeError):
            print(f"      ⚠️  Skipping row {index}: Cannot parse coordinates")
            return None

        # Create readable name
        name = f"{water_body} - {county} County Access"

        # Create description
        description = f"Public {access_type.lower()} access at {water_body} in {county} County, Texas. TPWD public access point."

        # Parse amenities (if columns exist)
        amenities = {
            'parking': row.get('PARKING', 'N').upper() == 'Y',
            'restrooms': row.get('RESTROOMS', 'N').upper() == 'Y',
            'lighting': row.get('LIGHTING', 'N').upper() == 'Y',
            'fish_cleaning': row.get('FISH_CLEAN', 'N').upper() == 'Y',
            'boat_trailer_parking': True,  # Assumed for boat ramps
            'camping': row.get('CAMPING', 'N').upper() == 'Y',
        }

        return FishingSpotData(
            name=name,
            latitude=latitude,
            longitude=longitude,
            county=county,
            water_body_name=water_body,
            spot_type='boat_ramp',
            description=description,
            state='TX',
            amenities=amenities,
            source_id=tpwaid,
            is_verified=True,
            meta_title=f"{water_body} Public Access - {county} County, Texas",
            meta_description=f"Public fishing access at {water_body} in {county} County. Free {access_type.lower()} access point with GPS coordinates."
        )


def main():
    """Example usage"""
    from config import RAW_DATA_DIR
    import os

    adapter = TexasTPWDAdapter()
    csv_path = os.path.join(RAW_DATA_DIR, 'tpwd_boat_ramps.csv')

    if not os.path.exists(csv_path):
        print(f"❌ File not found: {csv_path}")
        print(f"Please download TPWD boat ramps data and save as: {csv_path}")
        return

    rows_inserted = adapter.process_and_import(csv_path)
    print(f"\n✅ Import complete! {rows_inserted} spots added to database.")


if __name__ == "__main__":
    main()
