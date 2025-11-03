"""
Fix Kickerillo-Mischer entries

Both entries should be:
- Name: Kickerillo-Mischer Preserve
- Water Body: Marshall Lake
- Keep the better address (20215 Chasewood Park Dr., Houston)

Found 2 entries at similar locations (~0.5 miles apart):
- ID 2626: 29.9860700, -95.5639900
- ID 3247: 29.9878830, -95.5718435

These appear to be duplicates, so we'll update both to have consistent naming
and then manually verify if one should be deleted.
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
print("FIXING KICKERILLO-MISCHER ENTRIES")
print("="*70)
print()

# Get current entries
cur.execute("""
    SELECT id, name, water_body_name, address, latitude, longitude
    FROM fishing_spots
    WHERE id IN (2626, 3247)
    ORDER BY id
""")
current = cur.fetchall()

print("Current entries:")
for row in current:
    print(f"  ID {row['id']}: {row['name']}")
    print(f"    Water: {row['water_body_name']}")
    print(f"    Address: {row['address']}")
    print(f"    Coords: {row['latitude']}, {row['longitude']}")
    print()

# These are duplicates - delete ID 3247 (worse address), keep ID 2626
print("Action: Delete ID 3247 (duplicate), update ID 2626")
print()

# Delete the duplicate
cur.execute("DELETE FROM fishing_spots WHERE id = 3247")
print("✅ Deleted ID 3247 (duplicate)")

# Update the remaining entry
new_name = "Kickerillo-Mischer Preserve"
new_water_body = "Marshall Lake"
new_address = "20215 Chasewood Park Dr., Houston, TX 77070"

cur.execute("""
    UPDATE fishing_spots
    SET name = %s,
        water_body_name = %s,
        address = %s,
        slug = 'kickerillo-mischer-preserve-harris'
    WHERE id = 2626
""", (new_name, new_water_body, new_address))

print("✅ Updated ID 2626:")
print(f"  Name: {new_name}")
print(f"  Water Body: {new_water_body}")
print(f"  Address: {new_address}")
print()

conn.commit()

# Verify
cur.execute("""
    SELECT id, name, water_body_name, address, latitude, longitude
    FROM fishing_spots
    WHERE id = 2626
""")
updated = cur.fetchone()

print("="*70)
print("VERIFICATION")
print("="*70)
if updated:
    print(f"ID {updated['id']}: {updated['name']}")
    print(f"  Water: {updated['water_body_name']}")
    print(f"  Address: {updated['address']}")
    print(f"  Coords: {updated['latitude']}, {updated['longitude']}")
else:
    print("ERROR: Could not find updated entry!")
print()

conn.close()

print("="*70)
print("COMPLETE")
print("="*70)
print()
print("✅ Deleted duplicate entry (ID 3247)")
print("✅ Updated remaining entry (ID 2626)")
print("✅ Name is now 'Kickerillo-Mischer Preserve'")
print("✅ Water body is now 'Marshall Lake'")
