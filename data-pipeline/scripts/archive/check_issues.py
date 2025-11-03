"""
Check for additional duplicate/quality issues:
1. Willow Waterhole Unit entries (numbered)
2. Hackberry Park entries (one with null water body)
3. Nassau entries (incomplete name)
"""

import mysql.connector
import sys
import io
from math import radians, cos, sin, asin, sqrt

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.append('..')
from config import DB_CONFIG

def haversine(lon1, lat1, lon2, lat2):
    """Calculate distance in meters"""
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    return c * 6371000

conn = mysql.connector.connect(**DB_CONFIG)
cur = conn.cursor(dictionary=True)

print("="*70)
print("CHECKING DATA QUALITY ISSUES")
print("="*70)
print()

# 1. Willow Waterhole Unit entries
print("1. WILLOW WATERHOLE UNIT ENTRIES")
print("-" * 70)
cur.execute("""
    SELECT id, name, spot_type, county, water_body_name, latitude, longitude,
           data_source, parent_spot_id, is_parent
    FROM fishing_spots
    WHERE name LIKE '%Willow Waterhole%'
    ORDER BY name
""")

willow_entries = cur.fetchall()
print(f"Found {len(willow_entries)} entries:\n")

for entry in willow_entries:
    parent_info = ''
    if entry['parent_spot_id']:
        parent_info = f" (child of {entry['parent_spot_id']})"
    elif entry['is_parent']:
        parent_info = ' [PARENT]'

    print(f"ID {entry['id']}: {entry['name']}{parent_info}")
    print(f"  Type: {entry['spot_type']}, County: {entry['county']}")
    print(f"  Water: {entry['water_body_name']}")
    print(f"  Source: {entry['data_source']}")
    print(f"  Coords: {entry['latitude']}, {entry['longitude']}")
    print()

# Calculate distances between Willow entries
if len(willow_entries) > 1:
    print("Distances between Willow Waterhole entries:")
    for i in range(len(willow_entries)):
        for j in range(i+1, len(willow_entries)):
            e1 = willow_entries[i]
            e2 = willow_entries[j]
            dist = haversine(e1['longitude'], e1['latitude'],
                           e2['longitude'], e2['latitude'])
            print(f"  ID {e1['id']} <-> ID {e2['id']}: {dist:.1f}m")
    print()

print()

# 2. Hackberry Park entries
print("2. HACKBERRY PARK ENTRIES")
print("-" * 70)
cur.execute("""
    SELECT id, name, spot_type, county, water_body_name, latitude, longitude,
           data_source, parent_spot_id, is_parent
    FROM fishing_spots
    WHERE name LIKE '%Hackberry Park%'
    ORDER BY name
""")

hackberry_entries = cur.fetchall()
print(f"Found {len(hackberry_entries)} entries:\n")

for entry in hackberry_entries:
    parent_info = ''
    if entry['parent_spot_id']:
        parent_info = f" (child of {entry['parent_spot_id']})"
    elif entry['is_parent']:
        parent_info = ' [PARENT]'

    water_display = entry['water_body_name'] if entry['water_body_name'] else 'NULL'

    print(f"ID {entry['id']}: {entry['name']}{parent_info}")
    print(f"  Type: {entry['spot_type']}, County: {entry['county']}")
    print(f"  Water: {water_display}")
    print(f"  Source: {entry['data_source']}")
    print(f"  Coords: {entry['latitude']}, {entry['longitude']}")
    print()

# Calculate distances between Hackberry entries (excluding children)
hackberry_parents = [e for e in hackberry_entries if not e['parent_spot_id']]
if len(hackberry_parents) > 1:
    print("Distances between Hackberry Park entries (excluding children):")
    for i in range(len(hackberry_parents)):
        for j in range(i+1, len(hackberry_parents)):
            e1 = hackberry_parents[i]
            e2 = hackberry_parents[j]
            dist = haversine(e1['longitude'], e1['latitude'],
                           e2['longitude'], e2['latitude'])
            print(f"  ID {e1['id']} <-> ID {e2['id']}: {dist:.1f}m")
    print()

print()

# 3. Nassau entries
print("3. NASSAU ENTRIES")
print("-" * 70)
cur.execute("""
    SELECT id, name, spot_type, county, water_body_name, address, latitude, longitude, data_source
    FROM fishing_spots
    WHERE name = 'Nassau' OR name LIKE 'Nassau %'
    ORDER BY name
""")

nassau_entries = cur.fetchall()
print(f"Found {len(nassau_entries)} entries:\n")

for entry in nassau_entries:
    print(f"ID {entry['id']}: {entry['name']}")
    print(f"  Type: {entry['spot_type']}, County: {entry['county']}")
    print(f"  Water: {entry['water_body_name']}")
    print(f"  Address: {entry['address']}")
    print(f"  Source: {entry['data_source']}")
    print(f"  Coords: {entry['latitude']}, {entry['longitude']}")
    print()

conn.close()

print()
print("="*70)
print("SUMMARY")
print("="*70)
print(f"Willow Waterhole Unit entries: {len(willow_entries)}")
print(f"Hackberry Park entries: {len(hackberry_entries)} ({len(hackberry_parents)} parents)")
print(f"Nassau entries: {len(nassau_entries)}")
