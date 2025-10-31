"""
Base ETL Framework for Scalable Data Import

This module provides a flexible adapter pattern for importing fishing spot data
from various sources (state agencies, APIs, scraped data, user submissions).

Architecture:
- BaseDataAdapter: Abstract class defining the interface
- StateAdapter implementations: Texas, California, Florida, etc.
- Standardized output format for database insertion
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
import pandas as pd
from slugify import slugify
from db_utils import bulk_insert, check_duplicate_slug, find_nearby_spots, update_spot_if_better
import json


@dataclass
class FishingSpotData:
    """Standardized data structure for fishing spots"""
    name: str
    latitude: float
    longitude: float
    county: str  # or equivalent administrative unit
    water_body_name: str
    spot_type: str  # boat_ramp, pier, bank_fishing, state_park
    description: str
    state: str  # Two-letter state code (TX, CA, FL, etc.)

    # Optional fields
    amenities: Dict = None
    source_id: str = None  # Original ID from source system
    is_verified: bool = True
    meta_title: str = None
    meta_description: str = None
    address: str = None
    zip_code: str = None


class BaseDataAdapter(ABC):
    """
    Abstract base class for data adapters

    Each state/source implements this interface to transform their
    specific data format into our standardized FishingSpotData format.
    """

    def __init__(self, data_source_name: str, state_code: str, dedup_radius_meters: int = 100):
        """
        Initialize adapter

        Args:
            data_source_name: Name of data source (e.g., "TPWD_Boat_Ramps")
            state_code: Two-letter state code (e.g., "TX")
            dedup_radius_meters: Radius in meters to check for duplicates (default 100m)
        """
        self.data_source_name = data_source_name
        self.state_code = state_code
        self.dedup_radius_meters = dedup_radius_meters
        self.spots_processed = 0
        self.spots_updated = 0
        self.spots_skipped = 0
        self.errors = []

    @abstractmethod
    def load_data(self, file_path: str) -> pd.DataFrame:
        """
        Load data from source file

        Args:
            file_path: Path to data file (CSV, JSON, Excel, etc.)

        Returns:
            DataFrame containing raw data
        """
        pass

    @abstractmethod
    def transform_row(self, row: pd.Series, index: int) -> Optional[FishingSpotData]:
        """
        Transform a single row into standardized format

        Args:
            row: DataFrame row
            index: Row index (for error reporting)

        Returns:
            FishingSpotData object or None if row should be skipped
        """
        pass

    def generate_slug(self, spot: FishingSpotData) -> str:
        """
        Generate unique URL slug for fishing spot

        Args:
            spot: FishingSpotData object

        Returns:
            Unique slug string
        """
        # Use source_id if available for guaranteed uniqueness
        if spot.source_id:
            base = slugify(f"{spot.water_body_name}-{spot.county}-{spot.source_id}")
        else:
            base = slugify(f"{spot.water_body_name}-{spot.county}-{spot.state}")

        slug = base
        counter = 1

        while check_duplicate_slug(slug):
            slug = f"{base}-{counter}"
            counter += 1

        return slug

    def check_for_duplicate(self, spot: FishingSpotData) -> Optional[Dict]:
        """
        Check if a similar spot already exists nearby

        Args:
            spot: FishingSpotData to check

        Returns:
            Existing spot record if duplicate found, None otherwise
        """
        nearby_spots = find_nearby_spots(
            spot.latitude,
            spot.longitude,
            self.dedup_radius_meters
        )

        if nearby_spots:
            # Return the closest match
            return nearby_spots[0]

        return None

    def should_update_existing(self, existing: Dict, new_spot: FishingSpotData) -> bool:
        """
        Determine if new data is better than existing

        Args:
            existing: Existing database record
            new_spot: New FishingSpotData

        Returns:
            True if should update, False if should skip
        """
        # Update if new source has higher priority
        source_priority = {
            'Texas_State_Parks': 3,
            'Texas_Community_Lakes': 2,
            'TPWD_Boat_Ramps': 1,
        }

        existing_priority = source_priority.get(existing.get('data_source'), 0)
        new_priority = source_priority.get(self.data_source_name, 0)

        # Update if new source is higher priority
        if new_priority > existing_priority:
            return True

        # Update if new has richer data (more amenities, better description)
        if new_spot.amenities and len(new_spot.amenities) > 0:
            return True

        return False

    def to_database_record(self, spot: FishingSpotData, slug: str) -> Tuple:
        """
        Convert FishingSpotData to database tuple

        Args:
            spot: FishingSpotData object
            slug: Generated slug

        Returns:
            Tuple of values for database insertion
        """
        amenities_json = json.dumps(spot.amenities) if spot.amenities else None

        return (
            spot.name,
            slug,
            spot.latitude,
            spot.longitude,
            spot.county,
            spot.water_body_name,
            spot.spot_type,
            spot.description,
            amenities_json,
            self.data_source_name,
            spot.is_verified,
            spot.meta_title or f"{spot.name} - {spot.county} County, {spot.state}",
            spot.meta_description or f"Public fishing access at {spot.water_body_name} in {spot.county} County.",
            spot.state,
            spot.address,
            spot.zip_code
        )

    def process_and_import(self, file_path: str) -> int:
        """
        Full ETL pipeline: Extract, Transform, Load

        Args:
            file_path: Path to source data file

        Returns:
            Number of rows inserted
        """
        print(f"\n{'='*60}")
        print(f"Starting ETL: {self.data_source_name}")
        print(f"{'='*60}\n")

        # Extract
        print(f"[1/3] Loading data from: {file_path}")
        df = self.load_data(file_path)
        print(f"      Found {len(df)} records")

        # Transform
        print(f"\n[2/3] Transforming and checking for duplicates...")
        data_to_insert = []

        for idx, row in df.iterrows():
            try:
                spot = self.transform_row(row, idx)

                if spot is None:
                    continue  # Skip this row

                # Check for nearby duplicates
                existing = self.check_for_duplicate(spot)

                if existing:
                    # Found a duplicate - decide whether to update or skip
                    if self.should_update_existing(existing, spot):
                        # Update existing record with better data
                        import json as json_lib
                        update_data = {
                            'name': spot.name,
                            'description': spot.description,
                            'amenities': json_lib.dumps(spot.amenities) if spot.amenities else None,
                            'data_source': self.data_source_name,
                            'spot_type': spot.spot_type,
                        }
                        if update_spot_if_better(existing['id'], update_data):
                            self.spots_updated += 1
                            if (idx + 1) % 100 == 0:
                                print(f"      Updated duplicate: {spot.name} (within {existing['distance_meters']:.0f}m of existing)")
                    else:
                        # Skip - existing record is good enough
                        self.spots_skipped += 1
                        if (idx + 1) % 100 == 0:
                            print(f"      Skipped duplicate: {spot.name}")
                    continue

                # No duplicate - add to insert list
                slug = self.generate_slug(spot)
                record = self.to_database_record(spot, slug)
                data_to_insert.append(record)
                self.spots_processed += 1

                if (idx + 1) % 100 == 0:
                    print(f"      Processed {idx + 1}/{len(df)} records...")

            except Exception as e:
                error_msg = f"Row {idx}: {str(e)}"
                self.errors.append(error_msg)
                print(f"      ⚠️  Error: {error_msg}")

        print(f"      New records to insert: {self.spots_processed}")
        print(f"      Existing records updated: {self.spots_updated}")
        print(f"      Duplicates skipped: {self.spots_skipped}")

        # Load
        print(f"\n[3/3] Inserting into database...")

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
        print(f"✓ New records inserted: {rows_inserted}")
        print(f"✓ Existing records updated: {self.spots_updated}")
        print(f"  Duplicates skipped: {self.spots_skipped}")
        if self.errors:
            print(f"⚠  Errors encountered: {len(self.errors)}")
            print(f"   (Check logs for details)")
        print(f"{'='*60}\n")

        return rows_inserted
