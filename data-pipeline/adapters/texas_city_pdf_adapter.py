"""
Texas City Fishing Spots Adapter (from PDFs)

Imports fishing locations from parsed PDF data (Houston, Austin, DFW, San Antonio)
Uses forward geocoding to convert addresses to coordinates.

Data source: TPWD city fishing guides (parsed from PDFs)
"""

import pandas as pd
from typing import Optional
import sys
import os
import json
import time
import requests

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from etl_base import BaseDataAdapter, FishingSpotData


class TexasCityPdfAdapter(BaseDataAdapter):
    """Adapter for city fishing spots from PDF data"""

    def __init__(self, enable_osm_enrichment=True):
        super().__init__(
            data_source_name="Texas_City_PDFs",
            state_code="TX",
            enable_osm_enrichment=enable_osm_enrichment
        )

    def load_data(self, file_path: str) -> pd.DataFrame:
        """
        Load JSON data from parsed PDFs

        Args:
            file_path: Path to all_city_fishing_spots.json
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        df = pd.DataFrame(data)
        print(f"Loaded {len(df)} city fishing spots")

        return df

    def geocode_address(self, address: str, city: str) -> Optional[tuple]:
        """
        Forward geocode an address to lat/lon using Nominatim

        Args:
            address: Street address
            city: City name

        Returns:
            (lat, lon) tuple or None if geocoding fails
        """
        url = "https://nominatim.openstreetmap.org/search"

        # Build search query
        query = f"{address}, {city}, Texas"

        params = {
            'q': query,
            'format': 'json',
            'limit': 1,
            'addressdetails': 1
        }

        headers = {
            'User-Agent': 'FishingDirectoryBot/1.0 (Educational fishing access directory)'
        }

        try:
            # Rate limit: 1 request/second for Nominatim
            time.sleep(1.0)

            response = requests.get(url, params=params, headers=headers, timeout=10)
            response.raise_for_status()
            results = response.json()

            if results and len(results) > 0:
                lat = float(results[0]['lat'])
                lon = float(results[0]['lon'])
                return (lat, lon)
            else:
                print(f"      [WARN] No geocoding results for: {query}")
                return None

        except Exception as e:
            print(f"      [WARN] Geocoding failed for {query}: {e}")
            return None

    def transform_row(self, row: pd.Series, index: int) -> Optional[FishingSpotData]:
        """Transform city fishing spot row into standardized format"""

        name = row.get('name')
        address = row.get('address')
        city = row.get('city', 'Houston')  # Default to Houston if missing
        species = row.get('species', '')
        source_city = row.get('source_city', city.lower())

        if not name:
            print(f"      [WARN] Skipping entry {index}: No name")
            return None

        if not address:
            print(f"      [WARN] Skipping {name}: No address")
            return None

        # Geocode the address
        print(f"      Geocoding: {name} at {address}, {city}")
        coords = self.geocode_address(address, city)

        if not coords:
            print(f"      [WARN] Skipping {name}: Could not geocode address")
            return None

        latitude, longitude = coords
        print(f"      Found coords: {latitude}, {longitude}")

        # Determine county from city
        city_to_county = {
            'Houston': 'Harris',
            'Spring': 'Harris',
            'Katy': 'Harris',
            'Conroe': 'Montgomery',
            'Cypress': 'Harris',
            'Sugar Land': 'Fort Bend',
            'Missouri City': 'Fort Bend',
            'Pasadena': 'Harris',
            'Tomball': 'Harris',
            'Alvin': 'Brazoria',
            'Webster': 'Harris',
            'Friendswood': 'Harris',
            'Baytown': 'Harris',
            'Richmond': 'Fort Bend',
            'Rosenberg': 'Fort Bend',
            'Meadows Place': 'Fort Bend',
            'Pearland': 'Brazoria',
            'Needville': 'Fort Bend',
            'Austin': 'Travis',
            'Fort Worth': 'Tarrant',
            'Dallas': 'Dallas',
            'Arlington': 'Tarrant',
            'Grand Prairie': 'Dallas',
            'Irving': 'Dallas',
            'Plano': 'Collin',
            'Garland': 'Dallas',
            'San Antonio': 'Bexar',
        }

        county = city_to_county.get(city, city)  # Fallback to city name

        # Build description
        description = f"{name} is an urban fishing location in {city}. "

        if species:
            description += f"Target species include: {species}. "

        description += (
            "This location is featured in TPWD's city fishing guide, "
            "providing convenient access to fishing opportunities in the metro area."
        )

        # Basic amenities - we'll let OSM enrichment find more
        amenities = {}

        # Water body name - extract from name if possible
        # Many are like "Lake X", "X Park Lake", etc.
        water_body = name
        if ' Lake' in name or ' Pond' in name:
            water_body = name
        elif 'Park' in name:
            water_body = f"{name} Lake"

        # Meta data
        meta_title = f"{name} - {city} Fishing"
        meta_description = f"Fish at {name} in {city}. {species if species else 'Urban fishing access'} in the metro area."

        return FishingSpotData(
            name=name,
            latitude=latitude,
            longitude=longitude,
            county=county,
            water_body_name=water_body,
            spot_type='public_water',  # Urban fishing spots
            description=description,
            state='TX',
            amenities=amenities,
            address=address,
            source_id=str(row.get('number')),  # PDF entry number
            is_verified=True,
            meta_title=meta_title,
            meta_description=meta_description
        )


def main():
    """Run the adapter"""
    from config import RAW_DATA_DIR
    import os

    json_path = os.path.join(RAW_DATA_DIR, 'all_city_fishing_spots.json')

    if not os.path.exists(json_path):
        print(f"[ERROR] File not found: {json_path}")
        print("Run scripts/parse_city_fishing_pdfs.py first to generate the JSON file")
        return

    # Create adapter with OSM enrichment enabled
    adapter = TexasCityPdfAdapter(enable_osm_enrichment=True)

    # Use base class process_and_import which includes deduplication
    print()
    print("="*70)
    print("NOTE: This will take ~2 minutes due to geocoding rate limits")
    print("      (1 request/second for 111 locations)")
    print("="*70)
    print()

    rows_inserted = adapter.process_and_import(json_path)
    print(f"\n[SUCCESS] Complete! {rows_inserted} city fishing spots imported.")


if __name__ == "__main__":
    main()
