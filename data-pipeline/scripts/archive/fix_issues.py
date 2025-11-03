"""
Fix data quality issues:
1. Consolidate Willow Waterhole Unit 2-5 into parent entry
2. Delete duplicate Hackberry Park entry (ID 3281 with NULL water body)
3. Fix Nassau entry name (likely Nassau Bay)
"""

import mysql.connector
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.append('..')
from config import DB_CONFIG

conn = mysql.connector.connect(**DB_CONFIG)
cur = conn.cursor(dictionary=True)

print("="*70)
print("FIXING DATA QUALITY ISSUES")
print("="*70)
print()

# 1. Consolidate Willow Waterhole Units
print("1. CONSOLIDATING WILLOW WATERHOLE UNITS")
print("-" * 70)

# Get first child for coordinates
cur.execute("""
    SELECT latitude, longitude, county, state
    FROM fishing_spots
    WHERE id = 2657
""")
first_willow = cur.fetchone()

# Create parent entry
parent_name = "Willow Waterhole Greenway"
slug = "willow-waterhole-greenway-harris"
water_body = "Willow Waterhole Greenway"
description = "Public greenway with 4 fishing lakes (Willow, Prairie, Triangle, and Westbury)."

cur.execute("""
    INSERT INTO fishing_spots
    (name, slug, spot_type, county, state, latitude, longitude,
     water_body_name, description, data_source, is_parent, created_at, updated_at)
    VALUES (%s, %s, 'public_water', %s, %s, %s, %s, %s, %s, 'Manual_Consolidation', TRUE, NOW(), NOW())
""", (parent_name, slug, first_willow['county'], first_willow['state'],
      first_willow['latitude'], first_willow['longitude'],
      water_body, description))

parent_id = cur.lastrowid
print(f"✓ Created parent entry: {parent_name} (ID {parent_id})")

# Link children
willow_children = [2657, 2658, 2659, 2660]
for child_id in willow_children:
    cur.execute("""
        UPDATE fishing_spots
        SET parent_spot_id = %s, is_parent = FALSE
        WHERE id = %s
    """, (parent_id, child_id))

print(f"✓ Linked {len(willow_children)} Willow Waterhole units as children")
print()

# 2. Delete duplicate Hackberry Park entry
print("2. DELETING DUPLICATE HACKBERRY PARK")
print("-" * 70)

cur.execute("SELECT id, name, water_body_name FROM fishing_spots WHERE id = 3281")
dup_hackberry = cur.fetchone()
print(f"Deleting: ID {dup_hackberry['id']}: {dup_hackberry['name']} (water_body: {dup_hackberry['water_body_name']})")

cur.execute("DELETE FROM fishing_spots WHERE id = 3281")
print("✓ Deleted duplicate Hackberry Park entry with NULL water body")
print()

# 3. Fix Nassau entry name
print("3. FIXING NASSAU ENTRY NAME")
print("-" * 70)

cur.execute("SELECT id, name, water_body_name, county FROM fishing_spots WHERE id = 2645")
nassau = cur.fetchone()
print(f"Current: ID {nassau['id']}: {nassau['name']} (water: {nassau['water_body_name']})")

# Update to Nassau Bay
new_name = "Nassau Bay"
new_slug = "nassau-bay-harris"
cur.execute("""
    UPDATE fishing_spots
    SET name = %s, slug = %s, water_body_name = %s
    WHERE id = 2645
""", (new_name, new_slug, new_name))

print(f"✓ Updated to: {new_name}")
print()

conn.commit()

# Verification
print("="*70)
print("VERIFICATION")
print("="*70)
print()

print("Willow Waterhole entries:")
cur.execute("""
    SELECT id, name, parent_spot_id, is_parent
    FROM fishing_spots
    WHERE name LIKE '%Willow Waterhole%'
    ORDER BY CASE WHEN is_parent THEN 0 ELSE 1 END, name
""")
for row in cur.fetchall():
    parent_info = ''
    if row['parent_spot_id']:
        parent_info = f' (child of {row["parent_spot_id"]})'
    elif row['is_parent']:
        parent_info = ' [PARENT]'
    print(f"  ID {row['id']}: {row['name']}{parent_info}")
print()

print("Hackberry Park entries:")
cur.execute("""
    SELECT id, name, parent_spot_id, is_parent, water_body_name
    FROM fishing_spots
    WHERE name LIKE '%Hackberry Park%'
    ORDER BY CASE WHEN is_parent THEN 0 ELSE 1 END, name
""")
for row in cur.fetchall():
    parent_info = ''
    if row['parent_spot_id']:
        parent_info = f' (child of {row["parent_spot_id"]})'
    elif row['is_parent']:
        parent_info = ' [PARENT]'
    print(f"  ID {row['id']}: {row['name']}{parent_info}")
print()

print("Nassau entry:")
cur.execute("SELECT id, name, water_body_name FROM fishing_spots WHERE id = 2645")
nassau = cur.fetchone()
print(f"  ID {nassau['id']}: {nassau['name']} (water: {nassau['water_body_name']})")

conn.close()

print()
print("="*70)
print("COMPLETE")
print("="*70)
print()
print("✅ Consolidated Willow Waterhole Units (4 children)")
print("✅ Deleted duplicate Hackberry Park entry")
print("✅ Fixed Nassau entry name to Nassau Bay")
