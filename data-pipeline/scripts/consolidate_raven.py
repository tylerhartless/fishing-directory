"""
Consolidate Lake Raven duplicate entries

Found:
- ID 3165: Lake Raven (lake, Multiple Counties) - Texas_Major_Lakes
- ID 2959: Raven (public_water, Walker County) - Texas_Community_Lakes
- Distance: 0.0m (exact same coordinates)

Action: Delete ID 2959 as duplicate since lake entry is more authoritative
"""

import mysql.connector
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.append('..')
from config import DB_CONFIG

print("="*70)
print("CONSOLIDATING LAKE RAVEN DUPLICATE")
print("="*70)
print()

conn = mysql.connector.connect(**DB_CONFIG)
cur = conn.cursor(dictionary=True)

# Show entries before deletion
print("Current entries:")
cur.execute("""
    SELECT id, name, spot_type, county, data_source, latitude, longitude
    FROM fishing_spots
    WHERE id IN (3165, 2959)
    ORDER BY id
""")

entries = cur.fetchall()
for entry in entries:
    print(f"  ID {entry['id']}: {entry['name']} ({entry['spot_type']}, {entry['county']})")
    print(f"    Source: {entry['data_source']}")
    print(f"    Coords: {entry['latitude']}, {entry['longitude']}")
    print()

# Delete duplicate public_water entry
print("Deleting duplicate...")
cur.execute("DELETE FROM fishing_spots WHERE id = 2959")
print(f"✓ Deleted ID 2959 (Raven - public_water)")
print()

conn.commit()

# Verify
print("="*70)
print("VERIFICATION")
print("="*70)
print()

cur.execute("""
    SELECT id, name, spot_type, county
    FROM fishing_spots
    WHERE name LIKE '%Raven%'
    ORDER BY name
""")

remaining = cur.fetchall()
print(f"Remaining Raven entries: {len(remaining)}\n")

for spot in remaining:
    print(f"ID {spot['id']}: {spot['name']} ({spot['spot_type']}, {spot['county']})")

conn.close()

print()
print("="*70)
print("COMPLETE")
print("="*70)
print()
print("✅ Consolidated Lake Raven entries")
print("✅ Removed duplicate public_water entry")
print("✅ Lake entry (ID 3165) remains as authoritative source")
