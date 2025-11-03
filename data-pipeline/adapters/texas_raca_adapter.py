"""
Texas River Access and Conservation Areas (RACA) Adapter

Imports TPWD River Access and Conservation Areas from CSV data.
These are private lands leased by TPWD to provide public access to Texas rivers
for fishing, paddling, and recreation.

Data source: TPWD RACA database
"""

import pandas as pd
from typing import Optional
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from etl_base import BaseDataAdapter, FishingSpotData


class TexasRacaAdapter(BaseDataAdapter):
    """Adapter for Texas RACA sites from CSV"""

    def __init__(self, enable_osm_enrichment=False):
        super().__init__(
            data_source_name="Texas_RACA",
            state_code="TX",
            enable_osm_enrichment=enable_osm_enrichment
        )

    def load_data(self, file_path: str) -> pd.DataFrame:
        """
        Load CSV data

        Args:
            file_path: Path to River_Access_and_Conservation_Areas.csv
        """
        df = pd.read_csv(file_path, encoding='utf-8-sig')  # utf-8-sig to handle BOM
        print(f"Loaded {len(df)} RACA records")

        # Filter out rows with missing critical data
        initial_count = len(df)
        df = df.dropna(subset=['RACA_site_name', 'Latitude', 'Longitude'])
        filtered_count = len(df)

        if initial_count != filtered_count:
            print(f"Filtered out {initial_count - filtered_count} incomplete records")

        return df

    def transform_row(self, row: pd.Series, index: int) -> Optional[FishingSpotData]:
        """Transform RACA row into standardized format"""

        name = row.get('RACA_site_name')
        river_name = row.get('River', '')

        if not name:
            return None

        # Get coordinates
        try:
            latitude = float(row['Latitude'])
            longitude = float(row['Longitude'])

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

        # Extract county from description (many descriptions mention county)
        description_text = str(row.get('Description', '')).strip()
        county = self._extract_county_from_description(description_text)

        # If no county found, will be determined from coordinates during enrichment
        if not county:
            county = "Unknown"

        # Lease status
        lease_status = str(row.get('Lease_Status', '')).strip().lower()
        is_active = lease_status in ['current', 'Current']
        is_seasonal = lease_status == 'seasonal'

        # Build description
        description = f"{name} is a River Access and Conservation Area on the {river_name} River. "

        if is_seasonal:
            description += "This is a seasonal lease (typically for winter trout fishing). "

        description += "RACA sites are private lands leased by Texas Parks and Wildlife to provide public access to rivers for fishing, paddling, and recreation. "

        if description_text:
            description += description_text + " "

        # Add contact info if available
        if 'Phone:' in description_text:
            # Phone already in description
            pass

        directions = row.get('Directions', '')
        if directions and 'http' in str(directions):
            description += f"Directions: {directions}"

        # Amenities - most RACA sites are basic river access
        amenities = {
            'river_access': True
        }

        # Water body name is the river
        water_body = f"{river_name} River"

        # Meta data
        meta_title = f"{name} - {river_name} River Access"
        meta_description = f"Access the {river_name} River at {name}. Public river access for fishing and recreation through TPWD's RACA program."

        return FishingSpotData(
            name=name,
            latitude=latitude,
            longitude=longitude,
            county=county,
            water_body_name=water_body,
            spot_type='river_access',  # New type for RACA sites
            description=description,
            state='TX',
            amenities=amenities,
            source_id=row.get('OBJECTID'),
            is_verified=is_active,  # Only current leases are verified
            meta_title=meta_title,
            meta_description=meta_description
        )

    def _extract_county_from_description(self, description: str) -> Optional[str]:
        """
        Extract county name from description text

        Many descriptions end with "in [County Name] County"
        """
        import re

        # Pattern: "in [County] County" or "in [County] county"
        match = re.search(r'\bin\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\s+County', description, re.IGNORECASE)
        if match:
            county = match.group(1).strip()
            # Remove duplicate "County" if present
            county = county.replace(' County', '').replace(' county', '')
            return county

        return None


def main():
    """Run the adapter"""
    from config import RAW_DATA_DIR
    import os

    csv_path = os.path.join(RAW_DATA_DIR, 'River_Access_and_Conservation_Areas.csv')

    if not os.path.exists(csv_path):
        print(f"[ERROR] File not found: {csv_path}")
        return

    # Create adapter without OSM enrichment (most RACA sites are simple river access)
    adapter = TexasRacaAdapter(enable_osm_enrichment=False)

    # Use base class process_and_import which includes deduplication
    rows_inserted = adapter.process_and_import(csv_path)
    print(f"\n[SUCCESS] Complete! {rows_inserted} RACA sites imported.")


if __name__ == "__main__":
    main()
