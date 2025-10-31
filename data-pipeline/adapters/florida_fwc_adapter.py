"""
Florida Fish & Wildlife Conservation Commission (FWC) Data Adapter

Example adapter for Florida fishing access data.

Data Source: https://myfwc.com/fishing/saltwater/recreational/public-fishing-areas/
Format: Could be API, CSV, or web scraping
"""

import pandas as pd
from typing import Optional
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from etl_base import BaseDataAdapter, FishingSpotData


class FloridaFWCAdapter(BaseDataAdapter):
    """Adapter for Florida Fish & Wildlife Conservation Commission data"""

    def __init__(self):
        super().__init__(
            data_source_name="FWC_Public_Fishing_Areas",
            state_code="FL"
        )

    def load_data(self, file_path: str) -> pd.DataFrame:
        """Load Florida FWC data from CSV or JSON"""
        if file_path.endswith('.json'):
            return pd.read_json(file_path)
        return pd.read_csv(file_path)

    def transform_row(self, row: pd.Series, index: int) -> Optional[FishingSpotData]:
        """Transform Florida FWC row into standardized format"""

        name = row.get('name') or row.get('area_name') or f"Florida Fishing Access {index}"

        try:
            latitude = float(row.get('latitude') or row.get('lat'))
            longitude = float(row.get('longitude') or row.get('lon'))
        except (ValueError, TypeError):
            return None

        # Florida has 67 counties
        county = row.get('county') or 'Unknown'

        # Florida coastal areas
        water_body = row.get('water_body') or row.get('waterbody_name') or 'Florida Waters'

        # Check if saltwater or freshwater
        is_saltwater = 'saltwater' in str(row.get('water_type', '')).lower()

        # Determine spot type
        facility_type = str(row.get('facility_type', '')).lower()
        if 'pier' in facility_type or 'dock' in facility_type:
            spot_type = 'pier'
        elif 'ramp' in facility_type:
            spot_type = 'boat_ramp'
        else:
            spot_type = 'bank_fishing'

        # Description
        description = f"Public {'saltwater' if is_saltwater else 'freshwater'} fishing access at {water_body} in {county} County, Florida."

        if row.get('managed_by'):
            description += f" Managed by {row.get('managed_by')}."

        # Amenities
        amenities = {
            'parking': row.get('parking') == 'Yes' or row.get('parking') == True,
            'restrooms': row.get('restrooms') == 'Yes' or row.get('restrooms') == True,
            'boat_ramp': spot_type == 'boat_ramp',
            'pier': spot_type == 'pier',
            'fish_cleaning': row.get('cleaning_station') == 'Yes',
            'camping': row.get('camping') == 'Yes',
            'kayak_launch': row.get('kayak_access') == 'Yes',
        }

        return FishingSpotData(
            name=name,
            latitude=latitude,
            longitude=longitude,
            county=county,
            water_body_name=water_body,
            spot_type=spot_type,
            description=description,
            state='FL',
            amenities=amenities,
            source_id=row.get('site_id') or row.get('fwc_id'),
            is_verified=True,
            address=row.get('address'),
            zip_code=row.get('zip_code') or row.get('zipcode'),
            meta_title=f"{name} - {county} County, FL Fishing",
            meta_description=f"{'Saltwater' if is_saltwater else 'Freshwater'} fishing at {water_body}. Public access with GPS coordinates."
        )


def main():
    """Example usage"""
    import os
    from config import RAW_DATA_DIR

    adapter = FloridaFWCAdapter()
    csv_path = os.path.join(RAW_DATA_DIR, 'florida_fishing_access.csv')

    if not os.path.exists(csv_path):
        print(f"❌ File not found: {csv_path}")
        print(f"This is an example adapter for Florida FWC data.")
        return

    rows_inserted = adapter.process_and_import(csv_path)
    print(f"\n✅ Florida import complete! {rows_inserted} spots added.")


if __name__ == "__main__":
    main()
