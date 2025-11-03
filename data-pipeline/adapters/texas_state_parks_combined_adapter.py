"""
Texas State Parks Adapter - Combined Dataset

Merges two TPWD datasets:
1. point_of_interest.csv - Parks with fishing activity flag
2. public_building_structure.csv - Amenities and facilities

This provides rich amenity data for state parks with fishing access.
"""

import pandas as pd
from typing import Optional
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from etl_base import BaseDataAdapter, FishingSpotData


class TexasStateParksAdapter(BaseDataAdapter):
    """Adapter for Texas State Parks with combined amenity data"""

    def __init__(self):
        super().__init__(
            data_source_name="Texas_State_Parks",
            state_code="TX"
        )
        self.amenities_data = None

    def load_data(self, poi_path: str, amenities_path: str = None) -> pd.DataFrame:
        """
        Load and merge point of interest and amenities data

        Args:
            poi_path: Path to point_of_interest.csv
            amenities_path: Path to public_building_structure.csv (optional)
        """
        # Load main parks data
        df_parks = pd.read_csv(poi_path)

        print(f"Loaded {len(df_parks)} points of interest")
        print(f"Columns: {list(df_parks.columns)}")

        # Filter for parks with fishing activity
        # (Adjust column name based on actual CSV structure)
        if 'FISHING' in df_parks.columns:
            df_parks = df_parks[df_parks['FISHING'].str.upper() == 'Y']
        elif 'Activities' in df_parks.columns:
            df_parks = df_parks[df_parks['Activities'].str.contains('fishing', case=False, na=False)]

        print(f"Filtered to {len(df_parks)} parks with fishing")

        # Load and merge amenities if provided
        if amenities_path and os.path.exists(amenities_path):
            df_amenities = pd.read_csv(amenities_path)
            print(f"Loaded {len(df_amenities)} amenity records")
            print(f"Amenity columns: {list(df_amenities.columns)}")

            # Store for use in transform_row
            self.amenities_data = df_amenities

        return df_parks

    def get_park_amenities(self, park_name: str, park_id: str = None) -> dict:
        """
        Get amenities for a specific park from public_building_structure.csv

        Args:
            park_name: Name of the park
            park_id: Optional park ID for matching

        Returns:
            Dictionary of amenities
        """
        if self.amenities_data is None:
            return {}

        # Try to find amenities by park name or ID
        # Adjust column names based on actual CSV structure
        park_amenities = self.amenities_data[
            (self.amenities_data['PARK_NAME'] == park_name) |
            (self.amenities_data.get('PARK_ID') == park_id)
        ]

        amenities = {
            'restrooms': False,
            'fish_cleaning': False,
            'boat_ramp': False,
            'fishing_pier': False,
            'camping': False,
            'rv_hookups': False,
            'picnic_area': False,
            'parking': True,  # Assume all parks have parking
            'disabled_access': False,
        }

        # Check what facilities exist for this park
        for _, facility in park_amenities.iterrows():
            facility_type = str(facility.get('FACILITY_TYPE', '')).upper()

            if 'RESTROOM' in facility_type or 'BATHROOM' in facility_type:
                amenities['restrooms'] = True
            if 'FISH CLEAN' in facility_type or 'CLEANING' in facility_type:
                amenities['fish_cleaning'] = True
            if 'BOAT RAMP' in facility_type or 'LAUNCH' in facility_type:
                amenities['boat_ramp'] = True
            if 'PIER' in facility_type or 'DOCK' in facility_type:
                amenities['fishing_pier'] = True
            if 'CAMP' in facility_type:
                amenities['camping'] = True
            if 'RV' in facility_type or 'HOOKUP' in facility_type:
                amenities['rv_hookups'] = True
            if 'PICNIC' in facility_type:
                amenities['picnic_area'] = True
            if 'ADA' in facility_type or 'ACCESSIBLE' in facility_type:
                amenities['disabled_access'] = True

        return amenities

    def transform_row(self, row: pd.Series, index: int) -> Optional[FishingSpotData]:
        """Transform park row into standardized format"""

        # Get park name (adjust column name as needed)
        park_name = row.get('PARK_NAME') or row.get('NAME') or row.get('POI_NAME')

        if not park_name:
            print(f"      ⚠️  Skipping row {index}: No park name")
            return None

        # Get coordinates
        try:
            # Adjust column names based on actual CSV
            latitude = float(row.get('LATITUDE') or row.get('LAT') or row.get('Y'))
            longitude = float(row.get('LONGITUDE') or row.get('LON') or row.get('LONG') or row.get('X'))

            if latitude == 0 or longitude == 0:
                print(f"      ⚠️  Skipping {park_name}: Invalid coordinates")
                return None
        except (ValueError, TypeError):
            print(f"      ⚠️  Skipping {park_name}: Cannot parse coordinates")
            return None

        # Get county
        county = row.get('COUNTY') or row.get('COUNTY_NAME') or 'Unknown'

        # Get water body
        water_body = row.get('WATER_BODY') or row.get('WATERBODY') or 'Park waters'

        # Get amenities from linked dataset
        park_id = row.get('PARK_ID') or row.get('ID')
        amenities = self.get_park_amenities(park_name, park_id)

        # Build description highlighting FREE fishing
        description = self._build_description(park_name, county, water_body, amenities)

        return FishingSpotData(
            name=park_name,
            latitude=latitude,
            longitude=longitude,
            county=county,
            water_body_name=water_body,
            spot_type='state_park',
            description=description,
            state='TX',
            amenities=amenities,
            source_id=park_id,
            is_verified=True,
            address=row.get('ADDRESS'),
            zip_code=row.get('ZIP') or row.get('ZIPCODE'),
            meta_title=f"{park_name} - FREE Fishing (No License Required!)",
            meta_description=f"Fish for free at {park_name} in {county} County. No fishing license required at Texas State Parks!"
        )

    def _build_description(self, park_name: str, county: str, water_body: str, amenities: dict) -> str:
        """Create rich description from park data"""

        desc = f"{park_name} offers FREE fishing access at {water_body} in {county} County, Texas. "

        # Highlight key amenities
        features = []
        if amenities.get('boat_ramp'):
            features.append('boat ramp')
        if amenities.get('fishing_pier'):
            features.append('fishing pier')
        if amenities.get('fish_cleaning'):
            features.append('fish cleaning station')
        if amenities.get('camping'):
            features.append('camping')
        if amenities.get('picnic_area'):
            features.append('picnic area')
        if amenities.get('disabled_access'):
            features.append('ADA accessible facilities')

        if features:
            desc += f"Amenities include: {', '.join(features)}. "

        # Add the key selling point
        desc += "No fishing license required at Texas State Parks - bring your family and enjoy free fishing!"

        return desc

    def process_and_import(self, poi_path: str, amenities_path: str = None) -> int:
        """
        Override to accept two file paths

        Args:
            poi_path: Path to point_of_interest.csv
            amenities_path: Path to public_building_structure.csv
        """
        print(f"\n{'='*60}")
        print(f"Starting ETL: {self.data_source_name}")
        print(f"{'='*60}\n")

        # Extract
        print(f"[1/3] Loading data from: {poi_path}")
        if amenities_path:
            print(f"      Also loading amenities from: {amenities_path}")

        df = self.load_data(poi_path, amenities_path)
        print(f"      Found {len(df)} parks with fishing")

        # Transform and Load (using parent class method)
        data_to_insert = []

        print(f"\n[2/3] Transforming data...")
        for idx, row in df.iterrows():
            try:
                spot = self.transform_row(row, idx)

                if spot is None:
                    continue

                slug = self.generate_slug(spot)
                record = self.to_database_record(spot, slug)
                data_to_insert.append(record)
                self.spots_processed += 1

                if (idx + 1) % 10 == 0:
                    print(f"      Processed {idx + 1}/{len(df)} parks...")

            except Exception as e:
                error_msg = f"Row {idx}: {str(e)}"
                self.errors.append(error_msg)
                print(f"      ⚠️  Error: {error_msg}")

        print(f"      Transformed {self.spots_processed} parks")

        # Load
        print(f"\n[3/3] Inserting into database...")

        from db_utils import bulk_insert

        columns = [
            'name', 'slug', 'latitude', 'longitude', 'county', 'water_body_name',
            'spot_type', 'description', 'amenities', 'data_source', 'is_verified',
            'meta_title', 'meta_description', 'state', 'address', 'zip_code'
        ]

        rows_inserted = bulk_insert('fishing_spots', columns, data_to_insert)

        # Summary
        print(f"\n{'='*60}")
        print(f"ETL Complete: {self.data_source_name}")
        print(f"{'='*60}")
        print(f"✓ Parks processed: {self.spots_processed}")
        print(f"✓ Parks inserted:  {rows_inserted}")
        if self.errors:
            print(f"⚠  Errors encountered: {len(self.errors)}")
        print(f"{'='*60}\n")

        return rows_inserted


def main():
    """Example usage"""
    from config import RAW_DATA_DIR
    import os

    adapter = TexasStateParksAdapter()

    poi_path = os.path.join(RAW_DATA_DIR, 'point_of_interest.csv')
    amenities_path = os.path.join(RAW_DATA_DIR, 'public_building_structure.csv')

    if not os.path.exists(poi_path):
        print(f"❌ File not found: {poi_path}")
        print(f"\nPlease download from TPWD GIS portal and save as:")
        print(f"  {poi_path}")
        return

    if not os.path.exists(amenities_path):
        print(f"⚠️  Amenities file not found: {amenities_path}")
        print(f"   Will import parks without detailed amenity data")
        amenities_path = None

    rows_inserted = adapter.process_and_import(poi_path, amenities_path)
    print(f"\n✅ Texas State Parks import complete! {rows_inserted} parks added.")


if __name__ == "__main__":
    main()
