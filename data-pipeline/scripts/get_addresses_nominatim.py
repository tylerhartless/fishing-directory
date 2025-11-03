"""
Get addresses for fishing spots using reverse geocoding (Nominatim)
Focus on public_water spots that don't have addresses
"""

import mysql.connector
import sys
import io
from geopy.geocoders import Nominatim
import time

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.append('..')
from config import DB_CONFIG

# Initialize geocoder
geolocator = Nominatim(user_agent="fishing_directory_address_enrichment")

print("="*70)
print("ADDRESS ENRICHMENT - Reverse Geocoding")
print("="*70)
print()

# Connect to database
conn = mysql.connector.connect(**DB_CONFIG)
cur = conn.cursor(dictionary=True)

# Get spots without addresses
cur.execute("""
    SELECT id, name, spot_type, county, state, latitude, longitude, address
    FROM fishing_spots
    WHERE spot_type IN ('public_water', 'river_access')
      AND (address IS NULL OR address = '')
      AND (is_parent = TRUE OR parent_spot_id IS NULL)
    LIMIT 20
""")

spots = cur.fetchall()

print(f"Found {len(spots)} spots without addresses")
print(f"Testing reverse geocoding on first 20...")
print()

addresses_found = 0
addresses_failed = 0

for i, spot in enumerate(spots, 1):
    print(f"[{i}/{len(spots)}] {spot['name']} ({spot['county']} County)")
    print(f"  Coords: {spot['latitude']}, {spot['longitude']}")

    try:
        # Reverse geocode
        location = geolocator.reverse(f"{spot['latitude']}, {spot['longitude']}",
                                     exactly_one=True,
                                     language='en')

        if location and location.address:
            # Try to extract a useful address
            addr_parts = location.raw.get('address', {})

            # Build a sensible address
            address_parts = []

            # Add road/street if available
            if addr_parts.get('road'):
                address_parts.append(addr_parts['road'])
            elif addr_parts.get('hamlet'):
                address_parts.append(addr_parts['hamlet'])
            elif addr_parts.get('village'):
                address_parts.append(addr_parts['village'])

            # Add city
            if addr_parts.get('city'):
                address_parts.append(addr_parts['city'])
            elif addr_parts.get('town'):
                address_parts.append(addr_parts['town'])
            elif addr_parts.get('county'):
                address_parts.append(f"{addr_parts['county']} County")

            # Add state
            if addr_parts.get('state'):
                address_parts.append(addr_parts['state'])

            # Add ZIP if available
            if addr_parts.get('postcode'):
                address_parts.append(addr_parts['postcode'])

            if address_parts:
                final_address = ', '.join(address_parts)
                print(f"  Found: {final_address}")
                addresses_found += 1
            else:
                print(f"  No useful address data")
                addresses_failed += 1
        else:
            print(f"  No address found")
            addresses_failed += 1

    except Exception as e:
        print(f"  Error: {e}")
        addresses_failed += 1

    # Rate limiting - Nominatim requires 1 second between requests
    if i < len(spots):
        time.sleep(1.1)

    print()

print()
print("="*70)
print("SUMMARY")
print("="*70)
print()
print(f"Addresses found: {addresses_found}/{len(spots)}")
print(f"Failed: {addresses_failed}/{len(spots)}")
print()

if addresses_found > 10:
    print("Good success rate! Addresses can be obtained via reverse geocoding.")
    print()
    print("HOWEVER:")
    print("- Reverse geocoding gives generic addresses (nearby roads)")
    print("- Not the specific park/facility address")
    print("- Example: 'County Road 123' instead of '123 Park Entrance Dr'")
    print()
    print("BETTER APPROACH:")
    print("- Use Google Places API to find the actual facility")
    print("- Match by name + coordinates")
    print("- Get real business address from Places database")
    print()
    print("OR:")
    print("- Accept that water bodies don't need street addresses")
    print("- Coordinates are sufficient for navigation")
    print("- State parks already have addresses (100% coverage)")
else:
    print("Low success rate - many spots are in remote areas without addresses")

conn.close()
