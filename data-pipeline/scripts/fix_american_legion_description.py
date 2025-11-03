"""Fix American Legion Park Pond description"""
import sys
sys.path.insert(0, '..')
import mysql.connector
from config import DB_CONFIG

db_config = {k: v for k, v in DB_CONFIG.items() if k != 'cursorclass'}
conn = mysql.connector.connect(**db_config)
cur = conn.cursor(dictionary=True)

print("Fixing American Legion Park Pond description...\n")

# Find the entry
cur.execute("""
    SELECT id, name, description, spot_type
    FROM fishing_spots
    WHERE name = 'American Legion Park Pond'
    AND county = 'Fort Bend'
""")

spot = cur.fetchone()

if spot:
    print(f"Found: ID {spot['id']} - {spot['name']}")
    print(f"  Current description: {spot['description']}")
    print(f"  Spot type: {spot['spot_type']}")

    # Set appropriate description based on spot type
    new_description = "Public water access for fishing."

    cur.execute("""
        UPDATE fishing_spots
        SET description = %s
        WHERE id = %s
    """, (new_description, spot['id']))

    conn.commit()
    print(f"\n[OK] Updated description to: {new_description}")
else:
    print("Entry not found")

cur.close()
conn.close()
