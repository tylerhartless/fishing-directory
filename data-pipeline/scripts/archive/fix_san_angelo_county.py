"""
Fix San Angelo State Park county name

County should be "Tom Green" not "Tomgreen"
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
print("FIXING SAN ANGELO STATE PARK COUNTY")
print("="*70)
print()

# Get current entry
cur.execute("SELECT id, name, county FROM fishing_spots WHERE id = 1920")
current = cur.fetchone()

print("Current entry:")
print(f"  ID {current['id']}: {current['name']}")
print(f"  County: {current['county']}")
print()

# Update county
new_county = "Tom Green"

cur.execute("""
    UPDATE fishing_spots
    SET county = %s
    WHERE id = 1920
""", (new_county,))

print(f"Updated county to: {new_county}")
print()

conn.commit()

# Verify
cur.execute("SELECT id, name, county FROM fishing_spots WHERE id = 1920")
updated = cur.fetchone()

print("="*70)
print("VERIFICATION")
print("="*70)
print(f"ID {updated['id']}: {updated['name']}")
print(f"  County: {updated['county']}")

conn.close()

print()
print("="*70)
print("COMPLETE")
print("="*70)
print()
print("✅ Updated San Angelo State Park county")
print("✅ County is now 'Tom Green'")
