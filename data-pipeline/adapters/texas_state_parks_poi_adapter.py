"""
Texas State Parks Adapter - From Point of Interest Data

Works with TPWD's point_of_interest.csv which has individual features
rather than park-level data. Aggregates by ParkName.

Coordinates are in Web Mercator (EPSG:3857) and need conversion.
"""

import pandas as pd
from typing import Optional
import sys
import os
from pyproj import Transformer

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from etl_base import BaseDataAdapter, FishingSpotData


class TexasStateParksFromPOIAdapter(BaseDataAdapter):
    """Adapter for Texas State Parks from point_of_interest.csv"""

    def __init__(self):
        super().__init__(
            data_source_name="Texas_State_Parks",
            state_code="TX"
        )
        self.amenities_data = None
        # Transformer to convert Web Mercator (EPSG:3857) to WGS84 (EPSG:4326)
        self.transformer = Transformer.from_crs("EPSG:3857", "EPSG:4326", always_xy=True)

    def load_data(self, poi_path: str, amenities_path: str = None) -> pd.DataFrame:
        """
        Load POI data and aggregate by park, optionally merge amenities

        Args:
            poi_path: Path to point_of_interest.csv
            amenities_path: Path to public_building_structure.csv (optional)
        """
        df_poi = pd.read_csv(poi_path)
        print(f"Loaded {len(df_poi)} POI records")

        # Filter for fishing-related features
        fishing_keywords = ['fish', 'boat', 'pier', 'launch', 'ramp', 'dock']
        fishing_mask = df_poi['Name'].str.contains('|'.join(fishing_keywords), case=False, na=False)

        df_fishing = df_poi[fishing_mask]
        print(f"Found {len(df_fishing)} fishing-related POIs")

        # Get unique parks with fishing access
        # Group by ParkName and take first occurrence for coordinates
        df_parks = df_fishing.groupby('ParkName').first().reset_index()
        print(f"Aggregated to {len(df_parks)} unique parks with fishing")

        # Load amenities if provided
        if amenities_path and os.path.exists(amenities_path):
            self.amenities_data = pd.read_csv(amenities_path)
            print(f"Loaded {len(self.amenities_data)} amenity records")

        return df_parks

    def convert_coordinates(self, x: float, y: float) -> tuple:
        """
        Convert Web Mercator (EPSG:3857) to Lat/Lon (EPSG:4326)

        Args:
            x: X coordinate (easting)
            y: Y coordinate (northing)

        Returns:
            (longitude, latitude) tuple
        """
        lon, lat = self.transformer.transform(x, y)
        return lat, lon

    def get_park_amenities(self, park_name: str) -> dict:
        """Get amenities for a specific park"""
        if self.amenities_data is None:
            return {'parking': True}  # Minimal default

        # Filter amenities for this park
        park_amenities = self.amenities_data[
            self.amenities_data['ParkName'] == park_name
        ]

        amenities = {
            'restrooms': False,
            'fish_cleaning': False,
            'boat_ramp': False,
            'fishing_pier': False,
            'camping': False,
            'picnic_area': False,
            'parking': True,
        }

        # Check descriptors (use both Descriptor and Category)
        for _, facility in park_amenities.iterrows():
            desc = str(facility.get('Descriptor', '')).upper()

            if 'RESTROOM' in desc or 'BATHROOM' in desc:
                amenities['restrooms'] = True
            if 'FISH' in desc and 'CLEAN' in desc:
                amenities['fish_cleaning'] = True
            if 'BOAT' in desc or 'RAMP' in desc or 'LAUNCH' in desc:
                amenities['boat_ramp'] = True
            if 'PIER' in desc or 'DOCK' in desc:
                amenities['fishing_pier'] = True
            if 'CAMP' in desc:
                amenities['camping'] = True
            if 'PICNIC' in desc or 'PAVILION' in desc:
                amenities['picnic_area'] = True

        return amenities

    def transform_row(self, row: pd.Series, index: int) -> Optional[FishingSpotData]:
        """Transform park row into standardized format"""

        park_name = row.get('ParkName')
        if not park_name:
            return None

        # Convert coordinates from Web Mercator to Lat/Lon
        try:
            x = float(row['X'])
            y = float(row['Y'])
            latitude, longitude = self.convert_coordinates(x, y)

            # Sanity check
            if not (-100 < latitude < 36) or not (-107 < longitude < -93):
                print(f"      ⚠️  Skipping {park_name}: Coordinates outside Texas bounds")
                return None

        except (ValueError, TypeError) as e:
            print(f"      ⚠️  Skipping {park_name}: Cannot convert coordinates - {e}")
            return None

        # Get amenities for this park
        amenities = self.get_park_amenities(park_name)

        # Infer county from coordinates (you could add a lookup table later)
        # For now, we'll leave it as 'Unknown' or try to geocode
        county = 'Texas'  # Placeholder - ideally reverse geocode

        # Build description
        description = (
            f"{park_name} State Park offers fishing access with no fishing license required. "
            f"Texas State Parks waive the fishing license requirement for all anglers. "
        )

        # Add amenity details
        features = []
        if amenities.get('boat_ramp'):
            features.append('boat ramp')
        if amenities.get('fishing_pier'):
            features.append('fishing pier')
        if amenities.get('restrooms'):
            features.append('restrooms')
        if amenities.get('camping'):
            features.append('camping')

        if features:
            description += f"Amenities include: {', '.join(features)}."

        return FishingSpotData(
            name=f"{park_name} State Park",
            latitude=latitude,
            longitude=longitude,
            county=county,
            water_body_name='Park waters',
            spot_type='state_park',
            description=description,
            state='TX',
            amenities=amenities,
            source_id=str(row.get('OBJECTID')),
            is_verified=True,
            meta_title=f"{park_name} State Park - Fishing (No License Required)",
            meta_description=f"Fish at {park_name} State Park without a fishing license. Texas State Parks waive license requirements for all visitors."
        )

    def process_and_import(self, poi_path: str, amenities_path: str = None) -> int:
        """Process and import state parks"""
        print(f"\n{'='*60}")
        print(f"Starting ETL: {self.data_source_name}")
        print(f"{'='*60}\n")

        # Load data
        df = self.load_data(poi_path, amenities_path)

        if len(df) == 0:
            print("❌ No parks with fishing found!")
            return 0

        # Transform and load
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

            except Exception as e:
                error_msg = f"Row {idx}: {str(e)}"
                self.errors.append(error_msg)
                print(f"      ⚠️  Error: {error_msg}")

        print(f"      Transformed {self.spots_processed} parks")

        if len(data_to_insert) == 0:
            print("❌ No valid parks to insert!")
            return 0

        # Insert
        print(f"\n[3/3] Inserting into database...")

        from db_utils import bulk_insert

        columns = [
            'name', 'slug', 'latitude', 'longitude', 'county', 'water_body_name',
            'spot_type', 'description', 'amenities', 'data_source', 'is_verified',
            'meta_title', 'meta_description', 'state', 'address', 'zip_code'
        ]

        rows_inserted = bulk_insert('fishing_spots', columns, data_to_insert)

        print(f"\n{'='*60}")
        print(f"ETL Complete: {self.data_source_name}")
        print(f"{'='*60}")
        print(f"✓ Parks processed: {self.spots_processed}")
        print(f"✓ Parks inserted:  {rows_inserted}")
        if self.errors:
            print(f"⚠  Errors: {len(self.errors)}")
        print(f"{'='*60}\n")

        return rows_inserted


def main():
    """Run the adapter"""
    from config import RAW_DATA_DIR
    import os

    adapter = TexasStateParksFromPOIAdapter()

    poi_path = os.path.join(RAW_DATA_DIR, 'point_of_interest.csv')
    amenities_path = os.path.join(RAW_DATA_DIR, 'public_building_structure.csv')

    if not os.path.exists(poi_path):
        print(f"❌ File not found: {poi_path}")
        return

    if not os.path.exists(amenities_path):
        print(f"⚠️  Amenities file not found, will skip detailed amenities")
        amenities_path = None

    rows_inserted = adapter.process_and_import(poi_path, amenities_path)
    print(f"\n✅ Complete! {rows_inserted} state parks imported.")


if __name__ == "__main__":
    main()
