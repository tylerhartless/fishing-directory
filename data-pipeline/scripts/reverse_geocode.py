"""
Reverse Geocoding - Convert coordinates to addresses using Nominatim (OSM)

Usage:
    python scripts/reverse_geocode.py --spot-type river_access
    python scripts/reverse_geocode.py --limit 10 --dry-run
"""

import requests
import time
import sys
import os
import json
from typing import Dict, Optional

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from db_utils import get_connection


class ReverseGeocoder:
    """Reverse geocode coordinates to addresses using Nominatim"""

    def __init__(self):
        self.nominatim_url = "https://nominatim.openstreetmap.org/reverse"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'FishingDirectoryBot/1.0 (Educational fishing access directory)'
        })

    def geocode(self, lat: float, lon: float) -> Optional[Dict]:
        """
        Reverse geocode coordinates to an address

        Args:
            lat: Latitude
            lon: Longitude

        Returns:
            Dict with address components or None if failed
        """
        params = {
            'lat': lat,
            'lon': lon,
            'format': 'json',
            'addressdetails': 1,
            'zoom': 18  # Maximum detail level
        }

        try:
            # Rate limit: Nominatim allows 1 request/second
            time.sleep(1.0)

            response = self.session.get(
                self.nominatim_url,
                params=params,
                timeout=10
            )
            response.raise_for_status()
            data = response.json()

            if 'error' in data:
                return None

            # Extract address components
            address_data = data.get('address', {})

            # Build a formatted address
            parts = []

            # House number + street
            if address_data.get('house_number'):
                parts.append(address_data['house_number'])
            if address_data.get('road'):
                parts.append(address_data['road'])

            # City/town
            city = (address_data.get('city') or
                   address_data.get('town') or
                   address_data.get('village') or
                   address_data.get('hamlet'))

            # State
            state = address_data.get('state')

            # Zip code
            zipcode = address_data.get('postcode')

            # Build formatted address string
            street_address = ' '.join(parts) if parts else None

            result = {
                'display_name': data.get('display_name'),
                'street_address': street_address,
                'city': city,
                'county': address_data.get('county'),
                'state': state,
                'zip_code': zipcode,
                'country': address_data.get('country'),
                'raw_address': address_data
            }

            return result

        except requests.exceptions.RequestException as e:
            print(f"  [ERROR] Geocoding failed: {e}")
            return None
        except Exception as e:
            print(f"  [ERROR] Unexpected error: {e}")
            return None


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Reverse geocode fishing spots')
    parser.add_argument('--spot-type', help='Only geocode spots of this type (e.g., river_access)')
    parser.add_argument('--limit', type=int, default=10, help='Number of spots to geocode (default 10)')
    parser.add_argument('--dry-run', action='store_true', help='Show addresses without updating database')
    parser.add_argument('--county', help='Only geocode spots in specific county')
    args = parser.parse_args()

    print("="*70)
    print("Reverse Geocoding - Coordinates to Addresses")
    print("="*70)
    print()

    # Connect to database
    conn = get_connection(silent=True)
    cursor = conn.cursor(dictionary=True)

    # Build query
    where_clauses = []
    if args.spot_type:
        where_clauses.append(f"spot_type = '{args.spot_type}'")
    if args.county:
        where_clauses.append(f"county = '{args.county}'")

    # Only geocode spots without addresses
    where_clauses.append("(address IS NULL OR address = '')")

    where_clause = " AND ".join(where_clauses) if where_clauses else "1=1"

    query = f"""
        SELECT id, name, latitude, longitude, county, address
        FROM fishing_spots
        WHERE {where_clause}
        LIMIT {args.limit}
    """

    cursor.execute(query)
    spots = cursor.fetchall()

    if not spots:
        print("[INFO] No spots found matching criteria")
        cursor.close()
        conn.close()
        return

    print(f"[INFO] Found {len(spots)} spots to geocode")
    print()

    geocoder = ReverseGeocoder()

    success_count = 0
    fail_count = 0

    for spot in spots:
        print(f"Geocoding: {spot['name']}")
        print(f"  Location: {spot['latitude']}, {spot['longitude']}")

        result = geocoder.geocode(spot['latitude'], spot['longitude'])

        if result:
            print(f"  [+] Address found:")
            if result['street_address']:
                print(f"      Street: {result['street_address']}")
            if result['city']:
                print(f"      City: {result['city']}")
            if result['county']:
                print(f"      County: {result['county']}")
            if result['zip_code']:
                print(f"      ZIP: {result['zip_code']}")

            # Use street_address or fall back to display_name
            address = result['street_address'] or result['display_name']

            if not args.dry_run:
                # Update database
                update_cursor = conn.cursor()
                update_cursor.execute(
                    "UPDATE fishing_spots SET address = %s WHERE id = %s",
                    (address, spot['id'])
                )
                conn.commit()
                update_cursor.close()
                print(f"  [OK] Updated database")

            success_count += 1
        else:
            print(f"  [X] No address found")
            fail_count += 1

        print()

    cursor.close()
    conn.close()

    print("="*70)
    print("Geocoding Summary")
    print("="*70)
    print(f"Successfully geocoded: {success_count}")
    print(f"Failed: {fail_count}")
    if args.dry_run:
        print("[DRY RUN] No changes made to database")
    print("="*70)


if __name__ == "__main__":
    main()
