"""
Fix Lake Dabney entry

The lake is located at Lake Houston Wilderness Park.
- Update name to: Lake Houston Wilderness Park
- Keep water_body_name as: Lake Dabney
- Add address: 25840 FM 1485, New Caney, TX 77357
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
print("FIXING LAKE DABNEY ENTRY")
print("="*70)
print()

# Get current entry
cur.execute("SELECT id, name, water_body_name, address FROM fishing_spots WHERE id = 2810")
current = cur.fetchone()

print("Current entry:")
print(f"  ID {current['id']}: {current['name']}")
print(f"  Water: {current['water_body_name']}")
print(f"  Address: {current['address']}")
print()

# Update entry
new_name = "Lake Houston Wilderness Park"
new_address = "25840 FM 1485, New Caney, TX 77357"
water_body = "Lake Dabney"

cur.execute("""
    UPDATE fishing_spots
    SET name = %s,
        address = %s,
        slug = 'lake-houston-wilderness-park-montgomery'
    WHERE id = 2810
""", (new_name, new_address))

print("Updated to:")
print(f"  Name: {new_name}")
print(f"  Water Body: {water_body} (unchanged)")
print(f"  Address: {new_address}")
print()

conn.commit()

# Verify
cur.execute("SELECT id, name, water_body_name, address FROM fishing_spots WHERE id = 2810")
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
print("✅ Updated Lake Dabney entry")
print("✅ Location is now Lake Houston Wilderness Park")
print("✅ Water body remains Lake Dabney")
