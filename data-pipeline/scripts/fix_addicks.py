"""
Fix Addicks entry - should be Bear Creek Pioneers Park

The coordinates 29.7908, -95.6236 point to Bear Creek Pioneers Park,
not Addicks Reservoir itself. Bear Creek Pioneers Park is a large
county park with fishing ponds located near Addicks Reservoir.
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
print("FIXING ADDICKS ENTRY")
print("="*70)
print()

# Get current entry
cur.execute("SELECT id, name, water_body_name, slug FROM fishing_spots WHERE id = 2618")
current = cur.fetchone()

print("Current entry:")
print(f"  ID {current['id']}: {current['name']}")
print(f"  Water: {current['water_body_name']}")
print(f"  Slug: {current['slug']}")
print()

# Update to Bear Creek Pioneers Park
new_name = "Bear Creek Pioneers Park"
new_slug = "bear-creek-pioneers-park-harris"
new_water_body = "Bear Creek Pioneers Park"
new_description = "Large county park with fishing ponds near Addicks Reservoir."

cur.execute("""
    UPDATE fishing_spots
    SET name = %s,
        slug = %s,
        water_body_name = %s,
        description = %s
    WHERE id = 2618
""", (new_name, new_slug, new_water_body, new_description))

print("Updated to:")
print(f"  Name: {new_name}")
print(f"  Slug: {new_slug}")
print(f"  Water Body: {new_water_body}")
print(f"  Description: {new_description}")
print()

conn.commit()

# Verify
cur.execute("SELECT id, name, water_body_name, description FROM fishing_spots WHERE id = 2618")
updated = cur.fetchone()

print("="*70)
print("VERIFICATION")
print("="*70)
print(f"ID {updated['id']}: {updated['name']}")
print(f"  Water: {updated['water_body_name']}")
print(f"  Description: {updated['description']}")

conn.close()

print()
print("="*70)
print("COMPLETE")
print("="*70)
print()
print("✅ Updated Addicks entry to Bear Creek Pioneers Park")
print("✅ Coordinates point to the park, not the reservoir")
