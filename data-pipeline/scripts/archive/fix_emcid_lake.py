"""
Fix EMCID Lake entry

The lake is located at R.B. Tullis Library.
- Update name to: R.B. Tullis Library
- Keep water_body_name as: EMCID Lake
- Add address: 775 FM 1488, Conroe, TX 77384
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
print("FIXING EMCID LAKE ENTRY")
print("="*70)
print()

# Get current entry
cur.execute("SELECT id, name, water_body_name, address FROM fishing_spots WHERE id = 2806")
current = cur.fetchone()

print("Current entry:")
print(f"  ID {current['id']}: {current['name']}")
print(f"  Water: {current['water_body_name']}")
print(f"  Address: {current['address']}")
print()

# Update entry
new_name = "R.B. Tullis Library"
new_address = "775 FM 1488, Conroe, TX 77384"
water_body = "EMCID Lake"

cur.execute("""
    UPDATE fishing_spots
    SET name = %s,
        address = %s,
        slug = 'rb-tullis-library-montgomery'
    WHERE id = 2806
""", (new_name, new_address))

print("Updated to:")
print(f"  Name: {new_name}")
print(f"  Water Body: {water_body} (unchanged)")
print(f"  Address: {new_address}")
print()

conn.commit()

# Verify
cur.execute("SELECT id, name, water_body_name, address FROM fishing_spots WHERE id = 2806")
updated = cur.fetchone()

print("="*70)
print("VERIFICATION")
print("="*70)
print(f"ID {updated['id']}: {updated['name']}")
print(f"  Water: {updated['water_body_name']}")
print(f"  Address: {updated['address']}")

conn.close()

print()
print("="*70)
print("COMPLETE")
print("="*70)
print()
print("✅ Updated EMCID Lake entry")
print("✅ Location is now R.B. Tullis Library")
print("✅ Water body remains EMCID Lake")
