"""
Fix Burke-Crenshaw entries

Found two entries 106m apart:
- ID 3022: Burke Crenshaw Park (no hyphen, from Neighborhood Fishin)
- ID 2622: Burke-Crenshaw Lake (has hyphen, from Community Lakes, has address)

Solution:
- Keep ID 2622 as the main entry
- Update name to "Burke-Crenshaw Park" (the location)
- Keep water_body as "Burke-Crenshaw Lake"
- Delete ID 3022 as duplicate
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
print("FIXING BURKE-CRENSHAW ENTRIES")
print("="*70)
print()

# Get both entries
cur.execute("SELECT id, name, water_body_name, address FROM fishing_spots WHERE id IN (2622, 3022)")
entries = cur.fetchall()

print("Current entries:")
for entry in entries:
    print(f"  ID {entry['id']}: {entry['name']}")
    print(f"    Water: {entry['water_body_name']}")
    print(f"    Address: {entry['address']}")
    print()

# Update ID 2622 to have correct name
print("Updating ID 2622:")
print("  Name: 'Burke-Crenshaw Lake' → 'Burke-Crenshaw Park'")
print("  Water body: 'Burke-Crenshaw Lake' (kept)")

cur.execute("""
    UPDATE fishing_spots
    SET name = 'Burke-Crenshaw Park',
        slug = 'burke-crenshaw-park-harris'
    WHERE id = 2622
""")

print("✓ Updated\n")

# Delete ID 3022 as duplicate
print("Deleting ID 3022 (Burke Crenshaw Park - duplicate)")
cur.execute("DELETE FROM fishing_spots WHERE id = 3022")
print("✓ Deleted\n")

conn.commit()

# Verify
print("="*70)
print("VERIFICATION")
print("="*70)

cur.execute("SELECT id, name, water_body_name, address FROM fishing_spots WHERE id = 2622")
result = cur.fetchone()

print(f"ID {result['id']}: {result['name']}")
print(f"  Water Body: {result['water_body_name']}")
print(f"  Address: {result['address']}")

conn.close()

print()
print("="*70)
print("COMPLETE")
print("="*70)
print()
print("✅ Consolidated Burke-Crenshaw entries")
print("✅ Park is the location, Lake is the water body")
