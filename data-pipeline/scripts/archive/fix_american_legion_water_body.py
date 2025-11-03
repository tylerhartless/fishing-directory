"""Fix American Legion Park Pond water body name"""
import sys
sys.path.insert(0, '..')
import mysql.connector
from config import DB_CONFIG

db_config = {k: v for k, v in DB_CONFIG.items() if k != 'cursorclass'}
conn = mysql.connector.connect(**db_config)
cur = conn.cursor(dictionary=True)

print("Fixing American Legion Park Pond water body name...\n")

# Find the entry
cur.execute("""
    SELECT id, name, water_body_name, description
    FROM fishing_spots
    WHERE name = 'American Legion Park Pond'
    AND county = 'Fort Bend'
""")

spot = cur.fetchone()

if spot:
    print(f"Found: ID {spot['id']} - {spot['name']}")
    print(f"  Current water_body: {spot['water_body_name']}")
    print(f"  Current description: {spot['description']}")

    # Set water body name
    new_water_body = "American Legion Park Pond"

    cur.execute("""
        UPDATE fishing_spots
        SET water_body_name = %s
        WHERE id = %s
    """, (new_water_body, spot['id']))

    conn.commit()
    print(f"\n[OK] Updated water_body_name to: {new_water_body}")
else:
    print("Entry not found")

cur.close()
conn.close()
