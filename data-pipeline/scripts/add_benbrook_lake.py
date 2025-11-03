"""Add Benbrook Lake as a large lake entry"""
import sys
sys.path.insert(0, '..')
import mysql.connector
from config import DB_CONFIG
from slugify import slugify
import requests
import time

def reverse_geocode(lat, lon):
    """Reverse geocode coordinates to get county"""
    url = "https://nominatim.openstreetmap.org/reverse"
    params = {
        'lat': lat,
        'lon': lon,
        'format': 'json',
        'addressdetails': 1
    }
    headers = {'User-Agent': 'TexasFishingDirectory/1.0'}

    time.sleep(1.0)  # Rate limit

    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()

        address_data = data.get('address', {})
        county = address_data.get('county', '').replace(' County', '')
        return county
    except Exception as e:
        print(f"[WARN] Geocoding failed: {e}")
        return None

# Benbrook Lake info
name = "Benbrook Lake"
lat = 32.6234188
lon = -97.4923016

print(f"Adding {name}...")
print(f"  Coordinates: {lat}, {lon}")

# Get county from reverse geocoding
print(f"  Reverse geocoding to get county...")
county = reverse_geocode(lat, lon)
if not county:
    print("[ERROR] Could not determine county")
    sys.exit(1)

print(f"  County: {county}")

# Create slug
slug = slugify(name)

# Connect to database
db_config = {k: v for k, v in DB_CONFIG.items() if k != 'cursorclass'}
conn = mysql.connector.connect(**db_config)
cursor = conn.cursor()

# Check if already exists
cursor.execute("SELECT id FROM fishing_spots WHERE slug = %s", (slug,))
existing = cursor.fetchone()

if existing:
    print(f"[WARN] {name} already exists with ID {existing[0]}")
    cursor.close()
    conn.close()
    sys.exit(0)

# Insert Benbrook Lake
try:
    cursor.execute("""
        INSERT INTO fishing_spots (
            name, slug, latitude, longitude, county, water_body_name,
            spot_type, data_source, state, is_verified
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        name,
        slug,
        lat,
        lon,
        county,
        name,  # water_body_name is the same as name for large lakes
        'lake',  # Large lakes use 'lake' spot_type
        'Manual_Entry',
        'TX',
        False
    ))

    spot_id = cursor.lastrowid
    conn.commit()

    print(f"[OK] Added {name} with ID {spot_id}")

except Exception as e:
    print(f"[ERROR] Failed to add {name}: {e}")
    conn.rollback()

cursor.close()
conn.close()
