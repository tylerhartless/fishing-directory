#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Export fishing spots to JSON for Astro static build
Only exports non-boat-ramp, active spots for production
"""

import sys
import pymysql
import json
import os

# Ensure UTF-8 output on Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

MYSQL_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'fishing_user',
    'password': 'fishing_password',
    'database': 'fishing_directory'
}

print("Connecting to database...")
conn = pymysql.connect(**MYSQL_CONFIG)
cursor = conn.cursor(pymysql.cursors.DictCursor)

# Export only active, non-boat-ramp spots
print("Fetching spots...")
cursor.execute("""
    SELECT
        id,
        name,
        slug,
        latitude,
        longitude,
        county,
        water_body_name,
        spot_type,
        description,
        amenities,
        data_source,
        is_verified,
        meta_title,
        meta_description,
        created_at,
        updated_at
    FROM fishing_spots
    WHERE is_active = TRUE
    AND spot_type != 'boat_ramp'
    ORDER BY county, name
""")

spots = cursor.fetchall()

# Convert datetime objects to strings and Decimal to float
from decimal import Decimal

for spot in spots:
    if spot['created_at']:
        spot['created_at'] = spot['created_at'].isoformat()
    if spot['updated_at']:
        spot['updated_at'] = spot['updated_at'].isoformat()

    # Convert Decimal to float for latitude/longitude
    if isinstance(spot['latitude'], Decimal):
        spot['latitude'] = float(spot['latitude'])
    if isinstance(spot['longitude'], Decimal):
        spot['longitude'] = float(spot['longitude'])

    # Parse amenities JSON
    if spot['amenities']:
        if isinstance(spot['amenities'], str):
            spot['amenities'] = json.loads(spot['amenities'])
    else:
        spot['amenities'] = {}

    # Ensure all boolean fields are proper booleans
    spot['is_verified'] = bool(spot['is_verified'])

print(f"Exporting {len(spots)} spots...")

# Create output directory
os.makedirs('frontend/public/data', exist_ok=True)

# Write to JSON
output_file = 'frontend/public/data/fishing-spots.json'
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(spots, f, indent=2, ensure_ascii=False)

print(f"✓ Exported {len(spots)} spots to {output_file}")

# Show breakdown by type
cursor.execute("""
    SELECT spot_type, COUNT(*) as count
    FROM fishing_spots
    WHERE is_active = TRUE
    AND spot_type != 'boat_ramp'
    GROUP BY spot_type
    ORDER BY count DESC
""")

print("\nSpot breakdown:")
for row in cursor.fetchall():
    print(f"  {row['spot_type']}: {row['count']}")

conn.close()
print("\n✓ Export complete!")
