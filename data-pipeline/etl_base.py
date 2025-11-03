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
import html
import re
from difflib import SequenceMatcher


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

    def __init__(self, data_source_name: str, state_code: str, dedup_radius_meters: int = 100, enable_osm_enrichment: bool = False):
        """
        Initialize adapter

        Args:
            data_source_name: Name of data source (e.g., "TPWD_Boat_Ramps")
            state_code: Two-letter state code (e.g., "TX")
            dedup_radius_meters: Radius in meters to check for duplicates (default 100m)
            enable_osm_enrichment: Whether to enrich data with OSM information (default False)
        """
        self.data_source_name = data_source_name
        self.state_code = state_code
        self.dedup_radius_meters = dedup_radius_meters
        self.enable_osm_enrichment = enable_osm_enrichment
        self.spots_processed = 0
        self.spots_updated = 0
        self.spots_skipped = 0
        self.spots_enriched = 0
        self.errors = []

        # Lazy-load OSM enricher only if needed
        self._osm_enricher = None

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

    def clean_name(self, name: str) -> str:
        """
        Clean and normalize fishing spot names

        - Decodes HTML entities (including double-encoded)
        - Strips extra whitespace
        - Capitalizes properly

        Args:
            name: Raw name from data source

        Returns:
            Cleaned name string
        """
        if not name:
            return name

        # Decode HTML entities (double-encoded in some sources)
        cleaned = html.unescape(html.unescape(name))

        # Strip extra whitespace
        cleaned = ' '.join(cleaned.split())

        return cleaned

    def detect_numbered_pond_pattern(self, name: str) -> Optional[Tuple[str, str]]:
        """
        Detect if a name matches numbered pond pattern

        Patterns:
        - "Hackberry Park Pond 1" → ("Hackberry Park", "1")
        - "Jones Lake 3" → ("Jones Lake", "3")
        - "Willow Waterhole Unit 2" → ("Willow Waterhole", "2")

        Args:
            name: Spot name to check

        Returns:
            Tuple of (base_name, number) if pattern matches, None otherwise
        """
        # Pattern: base name + optional "Pond/Unit" + number
        patterns = [
            r'^(.+?)\s+Pond\s+#?(\d+)$',        # "Name Pond 1" or "Name Pond #1"
            r'^(.+?)\s+Unit\s+#?(\d+)$',        # "Name Unit 2"
            r'^(.+?)\s+#?(\d+)$',                # "Name 3" or "Name #3"
            r'^(.+?)\s+Lake\s+#?(\d+)$',        # "Name Lake 1"
        ]

        for pattern in patterns:
            match = re.match(pattern, name, re.IGNORECASE)
            if match:
                base_name = match.group(1).strip()
                number = match.group(2)
                return (base_name, number)

        return None

    def check_for_duplicate(self, spot: FishingSpotData) -> Optional[Dict]:
        """
        Check if a similar spot already exists nearby

        Uses spot type hierarchy and smart radius to determine duplicates:
        - state_park consolidates public_water (but NOT lake)
        - lake can coexist with state_park/public_water
        - public_water consolidates other public_water
        - boat_ramp stays separate from everything

        Smart radius approach:
        - Checks wider radius (500m) for better duplicate detection
        - Filters results based on name similarity + distance

        Args:
            spot: FishingSpotData to check

        Returns:
            Existing spot record if duplicate found, None otherwise
        """
        # Use larger radius for initial search (500m)
        # We'll filter by name similarity + distance below
        search_radius = max(500, self.dedup_radius_meters)

        nearby_spots = find_nearby_spots(
            spot.latitude,
            spot.longitude,
            search_radius
        )

        if not nearby_spots:
            return None

        # Define spot type hierarchy and consolidation rules
        def should_consolidate(new_type, existing_type):
            """
            Determine if new_type should consolidate with existing_type

            Returns True if they're duplicates, False if they should coexist
            """
            # Lakes always coexist with state_parks and public_water
            if new_type == 'lake' or existing_type == 'lake':
                return False

            # Boat ramps stay separate from everything
            if new_type == 'boat_ramp' or existing_type == 'boat_ramp':
                return False

            # State parks consolidate public_water
            if new_type == 'state_park' and existing_type == 'public_water':
                return True
            if existing_type == 'state_park' and new_type == 'public_water':
                return True

            # Same type always consolidates
            if new_type == existing_type:
                return True

            # River access and fishing piers consolidate with public_water
            if (new_type in ['river_access', 'fishing_pier'] and
                existing_type == 'public_water'):
                return True
            if (existing_type in ['river_access', 'fishing_pier'] and
                new_type == 'public_water'):
                return True

            # Default: don't consolidate
            return False

        # Helper function to calculate name similarity
        def name_similarity(name1, name2):
            """Calculate similarity ratio between two names (0.0 to 1.0)"""
            # Normalize names for comparison
            n1 = name1.lower().replace('-', ' ').replace("'", "")
            n2 = name2.lower().replace('-', ' ').replace("'", "")
            return SequenceMatcher(None, n1, n2).ratio()

        # Check each nearby spot with tiered distance thresholds
        for nearby in nearby_spots:
            distance = nearby['distance_meters']
            similarity = name_similarity(spot.name, nearby['name'])

            # Tiered thresholds based on name similarity:
            # 1. Same/very similar names (90%+) within 500m → likely duplicate
            # 2. Similar names (75%+) within 200m → likely duplicate
            # 3. Different names within 100m → check type hierarchy only

            should_check_consolidation = False

            if similarity >= 0.90 and distance <= 500:
                # Very similar names within 500m (e.g., "Burke-Crenshaw" vs "Burke Crenshaw")
                should_check_consolidation = True
            elif similarity >= 0.75 and distance <= 200:
                # Similar names within 200m
                should_check_consolidation = True
            elif distance <= 100:
                # Very close proximity regardless of name
                should_check_consolidation = True

            if should_check_consolidation and should_consolidate(spot.spot_type, nearby['spot_type']):
                # Found a duplicate
                return nearby

        return None

    def enrich_with_osm(self, spot: FishingSpotData) -> FishingSpotData:
        """
        Enrich spot data with OpenStreetMap information

        Queries OSM for:
        - Better water body names
        - Facility names and contact info
        - Amenities (parking, restrooms, etc.)

        Args:
            spot: FishingSpotData to enrich

        Returns:
            Enhanced FishingSpotData with OSM information
        """
        # Lazy-load OSM enricher
        if self._osm_enricher is None:
            from scripts.enrich_from_osm import OSMEnricher
            self._osm_enricher = OSMEnricher()

        # Build a spot dict for enricher
        spot_dict = {
            'id': spot.source_id or 'new',
            'name': spot.name,
            'water_body_name': spot.water_body_name,
            'county': spot.county,
            'latitude': spot.latitude,
            'longitude': spot.longitude
        }

        # Query OSM
        osm_result = self._osm_enricher.enrich_spot(spot_dict)

        if osm_result['status'] != 'success':
            # OSM query failed, return original spot
            return spot

        # Update water body name if OSM has a better one
        if osm_result.get('suggested_water_body'):
            spot.water_body_name = osm_result['suggested_water_body']

        # Update amenities with OSM data
        osm_amenities = osm_result.get('amenities', {})
        if spot.amenities is None:
            spot.amenities = {}

        # Merge OSM amenities (OSM data takes precedence)
        for amenity, has_it in osm_amenities.items():
            if has_it:
                spot.amenities[amenity] = True

        # Add facility info to description if available
        if osm_result.get('facility_name'):
            facility_name = osm_result['facility_name']
            # Only update if facility name differs from spot name
            if facility_name.lower() not in spot.name.lower():
                # Prepend facility context to description
                facility_info = f"Located at {facility_name}. "
                if osm_result.get('facility_website'):
                    facility_info += f"Visit {osm_result['facility_website']} for more details. "

                spot.description = facility_info + spot.description

        self.spots_enriched += 1
        return spot

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

                # Enrich with OSM data if enabled
                if self.enable_osm_enrichment:
                    import time
                    spot = self.enrich_with_osm(spot)
                    # Rate limiting - OSM requests max 2 per second
                    time.sleep(0.6)

                # Check for nearby duplicates
                existing = self.check_for_duplicate(spot)

                if existing:
                    # Found a duplicate - decide whether to update or skip
                    if self.should_update_existing(existing, spot):
                        # Update existing record with better data
                        import json as json_lib

                        # Determine source priorities
                        source_priority = {
                            'Texas_State_Parks': 3,
                            'Texas_Community_Lakes': 2,
                            'TPWD_Boat_Ramps': 1,
                        }
                        existing_priority = source_priority.get(existing.get('data_source'), 0)
                        new_priority = source_priority.get(self.data_source_name, 0)

                        # Merge amenities from both sources
                        existing_amenities = json_lib.loads(existing.get('amenities')) if existing.get('amenities') else {}
                        new_amenities = spot.amenities if spot.amenities else {}

                        # Add spot type as amenity if merging lower-priority type into higher-priority
                        if new_priority < existing_priority and spot.spot_type:
                            # Adding boat_ramp to state_park, for example
                            new_amenities[spot.spot_type] = True
                        elif new_priority > existing_priority and existing.get('spot_type'):
                            # Adding state_park amenity when boat_ramp gets upgraded
                            new_amenities[existing.get('spot_type')] = True

                        # Merge amenities (new values override existing)
                        merged_amenities = {**existing_amenities, **new_amenities}

                        # Prepare update data
                        update_data = {
                            'amenities': json_lib.dumps(merged_amenities) if merged_amenities else None,
                        }

                        # Always enrich with address if new spot has one and existing doesn't
                        if spot.address and not existing.get('address'):
                            update_data['address'] = spot.address
                            if spot.zip_code:
                                update_data['zip_code'] = spot.zip_code

                        # Only update spot_type if new source has higher priority
                        if new_priority > existing_priority:
                            update_data['spot_type'] = spot.spot_type
                            update_data['name'] = spot.name
                            update_data['description'] = spot.description
                            update_data['data_source'] = self.data_source_name

                            # Only update water_body_name if new one is better than existing
                            # Prefer specific water body names over generic or bad names
                            new_wb = spot.water_body_name
                            existing_wb = existing.get('water_body_name', '')

                            # Don't update if existing has "State Park" in it (bad boat ramp data)
                            # Always override this, even with "Park Waters"
                            if 'State Park' in existing_wb:
                                update_data['water_body_name'] = new_wb  # Override bad boat ramp data
                            # Don't update if new one is generic "Park Waters" (and existing is good)
                            elif new_wb == 'Park Waters':
                                pass  # Keep existing (boat ramp likely has better name)
                            # Don't update if new one has "Unit" (park unit designation)
                            elif 'Unit' in new_wb and existing_wb:
                                pass  # Keep existing
                            # Prefer names with "Reservoir", "Lake", "Bay" over others
                            elif any(keyword in existing_wb for keyword in ['Reservoir', 'Lake', 'Bay']) and \
                                 not any(keyword in new_wb for keyword in ['Reservoir', 'Lake', 'Bay']):
                                pass  # Keep existing (it's more specific)
                            else:
                                # New name is better, update it
                                update_data['water_body_name'] = new_wb

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
                print(f"      [ERROR] {error_msg}")

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
        print(f"[OK] New records inserted: {rows_inserted}")
        print(f"[OK] Existing records updated: {self.spots_updated}")
        print(f"  Duplicates skipped: {self.spots_skipped}")
        if self.enable_osm_enrichment:
            print(f"[OK] Records enriched with OSM: {self.spots_enriched}")
        if self.errors:
            print(f"[WARN] Errors encountered: {len(self.errors)}")
            print(f"   (Check logs for details)")
        print(f"{'='*60}\n")

        return rows_inserted
