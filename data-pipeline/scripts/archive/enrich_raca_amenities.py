"""
Enrich RACA sites with parking lot and gate information

Uses RACA_Gates_ParkingLots_pnts.csv to:
1. Add parking/gate amenities
2. Update coordinates to parking lot location (where people actually drive to)
3. Reverse geocode parking lot location for accurate addresses
"""

import sys
import os
import pandas as pd
import json
import time
import requests
from pyproj import Transformer

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from db_utils import get_connection


def web_mercator_to_latlon(x, y):
    """Convert Web Mercator (EPSG:3857) to WGS84 lat/lon"""
    # EPSG:3857 is (x=lon, y=lat) in meters
    # EPSG:4326 is (lon, lat) in degrees
    # Transformer.transform returns (lon, lat) when going from 3857 to 4326
    transformer = Transformer.from_crs("EPSG:3857", "EPSG:4326", always_xy=True)
    lon, lat = transformer.transform(x, y)
    return lat, lon


def reverse_geocode(lat, lon):
    """Reverse geocode coordinates to address using Nominatim"""
    url = "https://nominatim.openstreetmap.org/reverse"
    params = {
        'lat': lat,
        'lon': lon,
        'format': 'json',
        'addressdetails': 1,
        'zoom': 18
    }

    headers = {
        'User-Agent': 'FishingDirectoryBot/1.0 (Educational fishing access directory)'
    }

    try:
        # Rate limit: 1 request/second
        time.sleep(1.0)

        response = requests.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()

        if 'error' in data:
            print(f"      [DEBUG] API returned error: {data.get('error')}")
            return None

        if not data:
            print(f"      [DEBUG] API returned empty data")
            return None

        address_data = data.get('address', {})
        if not address_data:
            print(f"      [DEBUG] No address in response. Response keys: {list(data.keys())}")

        # Build formatted address
        parts = []
        if address_data.get('house_number'):
            parts.append(address_data['house_number'])
        if address_data.get('road'):
            parts.append(address_data['road'])

        street_address = ' '.join(parts) if parts else None

        return {
            'display_name': data.get('display_name'),
            'street_address': street_address,
            'city': (address_data.get('city') or
                    address_data.get('town') or
                    address_data.get('village')),
            'county': address_data.get('county'),
            'zip_code': address_data.get('postcode')
        }

    except Exception as e:
        print(f"      [WARN] Geocoding failed: {e}")
        return None


def extract_raca_name(feature_name):
    """
    Extract RACA site name from feature name

    Examples:
    - "John Knox Ranch Entry Gate" -> "John Knox Ranch"
    - "Maso Llan Rd Parking Lot" -> "Maso Llan Rd Access"
    """
    # Remove common suffixes
    for suffix in [' Entry Gate', ' River Gate', ' Parking Lot', ' Parking', ' Access Area Parking Lot', ' Access Parking']:
        if feature_name.endswith(suffix):
            return feature_name[:-len(suffix)].strip()

    return feature_name


def main():
    csv_path = "../../raw-data/RACA_Gates_ParkingLots_pnts.csv"

    if not os.path.exists(csv_path):
        print(f"[ERROR] File not found: {csv_path}")
        return

    print("="*70)
    print("Enriching RACA Sites with Parking/Gate Amenities")
    print("="*70)
    print()

    # Load parking/gate data
    df = pd.read_csv(csv_path, encoding='utf-8-sig')
    print(f"[OK] Loaded {len(df)} parking/gate entries")
    print()

    # Group by RACA site and extract parking lot coordinates
    site_data = {}

    for _, row in df.iterrows():
        feature_type = row['FeatureType']
        feature_name = row['FeatureName']
        x = row['X']
        y = row['Y']

        # Extract RACA site name
        raca_name = extract_raca_name(feature_name)

        if raca_name not in site_data:
            site_data[raca_name] = {
                'parking': False,
                'gate': False,
                'parking_lat': None,
                'parking_lon': None
            }

        if feature_type == 'Parking Lot':
            site_data[raca_name]['parking'] = True
            # Convert Web Mercator to lat/lon
            lat, lon = web_mercator_to_latlon(x, y)
            site_data[raca_name]['parking_lat'] = lat
            site_data[raca_name]['parking_lon'] = lon
        elif feature_type == 'Gate':
            site_data[raca_name]['gate'] = True

    print(f"[OK] Found amenities for {len(site_data)} RACA sites")
    print()

    # Connect to database
    conn = get_connection(silent=True)
    cursor = conn.cursor(dictionary=True)

    # Get all RACA sites
    cursor.execute("""
        SELECT id, name, amenities
        FROM fishing_spots
        WHERE spot_type = 'river_access'
    """)

    raca_sites = cursor.fetchall()
    print(f"[OK] Found {len(raca_sites)} RACA sites in database")
    print()

    # Match and update
    matched_count = 0
    updated_count = 0

    for site in raca_sites:
        # Try to match by name
        matched = False
        matched_data = None

        # Try exact match first
        if site['name'] in site_data:
            matched = True
            matched_data = site_data[site['name']]
        else:
            # Try fuzzy matching
            for site_name in site_data.keys():
                if site_name in site['name'] or site['name'] in site_name:
                    matched = True
                    matched_data = site_data[site_name]
                    break

        if matched:
            matched_count += 1

            # Load existing amenities
            if site['amenities']:
                existing_amenities = json.loads(site['amenities'])
            else:
                existing_amenities = {}

            # Extract amenities only (no coords)
            amenities_to_add = {
                'parking': matched_data['parking'],
                'gate': matched_data['gate']
            }

            # Merge amenities
            updated_amenities = {**existing_amenities, **amenities_to_add}

            # Prepare update fields
            update_fields = []
            update_values = []

            # Update amenities if changed
            if updated_amenities != existing_amenities:
                update_fields.append("amenities = %s")
                update_values.append(json.dumps(updated_amenities))

            # Update coordinates if parking lot coordinates exist
            if matched_data['parking_lat'] and matched_data['parking_lon']:
                update_fields.append("latitude = %s")
                update_fields.append("longitude = %s")
                update_values.append(matched_data['parking_lat'])
                update_values.append(matched_data['parking_lon'])

                # Reverse geocode to get address
                print(f"[*] {site['name']}: Updating coordinates and geocoding...")
                print(f"    Calling reverse_geocode({matched_data['parking_lat']}, {matched_data['parking_lon']})")
                address_data = reverse_geocode(matched_data['parking_lat'], matched_data['parking_lon'])
                print(f"    Geocode result: {address_data}")

                if address_data:
                    address = address_data['street_address'] or address_data['display_name']
                    update_fields.append("address = %s")
                    update_values.append(address)
                    print(f"    Parking lot address: {address}")
                else:
                    print(f"    [WARN] No address data returned")

            # Perform update if there are changes
            if update_fields:
                update_values.append(site['id'])
                update_sql = f"UPDATE fishing_spots SET {', '.join(update_fields)} WHERE id = %s"

                update_cursor = conn.cursor()
                update_cursor.execute(update_sql, tuple(update_values))
                conn.commit()
                update_cursor.close()

                amenity_list = [k for k, v in updated_amenities.items() if v]
                print(f"[+] Updated {site['name']}: {', '.join(amenity_list)}")
                updated_count += 1
            else:
                print(f"[=] {site['name']}: No changes needed")

    cursor.close()
    conn.close()

    print()
    print("="*70)
    print("Summary")
    print("="*70)
    print(f"RACA sites in database: {len(raca_sites)}")
    print(f"Sites matched with amenities: {matched_count}")
    print(f"Sites updated: {updated_count}")
    print("="*70)


if __name__ == "__main__":
    main()
