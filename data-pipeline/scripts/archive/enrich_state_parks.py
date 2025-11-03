"""
Enrich state parks with addresses using reverse geocoding and fix data quality issues
"""
import sys
sys.path.insert(0, '..')
import mysql.connector
from config import DB_CONFIG
import time
import requests
from typing import Optional, Dict

def reverse_geocode(lat: float, lon: float) -> Optional[Dict]:
    """Reverse geocode coordinates to an address using Nominatim"""
    url = "https://nominatim.openstreetmap.org/reverse"

    params = {
        'lat': lat,
        'lon': lon,
        'format': 'json',
        'addressdetails': 1,
        'zoom': 18
    }

    headers = {
        'User-Agent': 'TexasFishingDirectory/1.0'
    }

    # Rate limit: 1 request/second
    time.sleep(1.0)

    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()

        address_data = data.get('address', {})

        # Try to build a street address
        house_number = address_data.get('house_number')
        road = address_data.get('road')
        street_address = None

        if house_number and road:
            street_address = f"{house_number} {road}"
        elif road:
            street_address = road

        city = address_data.get('city') or address_data.get('town') or address_data.get('village')
        county = address_data.get('county')
        postcode = address_data.get('postcode')

        return {
            'street_address': street_address,
            'display_name': data.get('display_name'),
            'city': city,
            'county': county,
            'zip_code': postcode
        }

    except Exception as e:
        print(f"  [ERROR] Geocoding failed: {e}")
        return None

def main():
    db_config = {k: v for k, v in DB_CONFIG.items() if k != 'cursorclass'}
    conn = mysql.connector.connect(**db_config)
    cur = conn.cursor(dictionary=True)

    # Get all state parks without addresses
    cur.execute("""
        SELECT id, name, latitude, longitude, water_body_name
        FROM fishing_spots
        WHERE data_source LIKE '%state_park%'
        AND (address IS NULL OR address = '')
        ORDER BY name
    """)

    parks = cur.fetchall()
    print(f'Found {len(parks)} state parks without addresses\n')

    # Manual fixes for known issues
    manual_fixes = {
        'Abilene State Park': {
            'water_body_name': 'Lake Abilene'
        },
        'Daingerfield State Park': {
            'water_body_name': 'Daingerfield State Park Lake'
        },
        'Cleburne State Park': {
            'water_body_name': 'Cedar Lake'
        }
    }

    updated_count = 0

    for park in parks:
        print(f"Processing: {park['name']}")

        # Reverse geocode to get address
        address_data = reverse_geocode(park['latitude'], park['longitude'])

        update_fields = []
        update_values = []

        if address_data:
            address = address_data['street_address'] or address_data['display_name']
            if address:
                update_fields.append("address = %s")
                update_values.append(address)
                print(f"  Address: {address}")

            if address_data['zip_code']:
                update_fields.append("zip_code = %s")
                update_values.append(address_data['zip_code'])
                print(f"  Zip: {address_data['zip_code']}")

        # Apply manual fixes if applicable
        if park['name'] in manual_fixes:
            fixes = manual_fixes[park['name']]
            if 'water_body_name' in fixes:
                update_fields.append("water_body_name = %s")
                update_values.append(fixes['water_body_name'])
                print(f"  Water body fixed: {park['water_body_name']} -> {fixes['water_body_name']}")

        # Update the record
        if update_fields:
            sql = f"UPDATE fishing_spots SET {', '.join(update_fields)} WHERE id = %s"
            update_values.append(park['id'])

            cur.execute(sql, update_values)
            conn.commit()
            updated_count += 1
            print(f"  [OK] Updated\n")
        else:
            print(f"  No updates needed\n")

    print(f"\n{'='*60}")
    print(f"Summary: Updated {updated_count} state parks")
    print(f"{'='*60}")

    conn.close()

if __name__ == '__main__':
    main()
