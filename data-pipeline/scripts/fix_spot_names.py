"""Fix specific spot names and water body separations"""
import sys
sys.path.insert(0, '..')
import mysql.connector
from config import DB_CONFIG

db_config = {k: v for k, v in DB_CONFIG.items() if k != 'cursorclass'}
conn = mysql.connector.connect(**db_config)
cur = conn.cursor(dictionary=True)

print("Fixing spot names and water body separations...\n")

# Fix 1: Albert Sallas -> A.V. 'Bull' Sallas Park
print("1. Checking Albert Sallas County Park...")
cur.execute("""
    SELECT id, name, water_body_name, description
    FROM fishing_spots
    WHERE name LIKE '%Albert Sallas%' OR name LIKE '%Sallas%'
""")
sallas_spots = cur.fetchall()

if sallas_spots:
    for spot in sallas_spots:
        print(f"   Found: ID {spot['id']} - {spot['name']}")
        print(f"   Description: {spot['description'][:100] if spot['description'] else 'None'}...")

        # Update to Bull Sallas name
        cur.execute("""
            UPDATE fishing_spots
            SET name = %s
            WHERE id = %s
        """, ("A.V. 'Bull' Sallas Park", spot['id']))
        print(f"   [OK] Updated to: A.V. 'Bull' Sallas Park\n")
else:
    print("   Not found\n")

# Fix 2: Alexander Deussen Park on Lake Houston -> separate park and water body
print("2. Checking Alexander Deussen Park on Lake Houston...")
cur.execute("""
    SELECT id, name, water_body_name
    FROM fishing_spots
    WHERE name LIKE '%Alexander Deussen%' OR name LIKE '%Deussen%'
""")
deussen_spots = cur.fetchall()

if deussen_spots:
    for spot in deussen_spots:
        print(f"   Found: ID {spot['id']} - {spot['name']}")
        print(f"   Current water_body: {spot['water_body_name']}")

        # Update to separate park name and water body
        cur.execute("""
            UPDATE fishing_spots
            SET name = %s,
                water_body_name = %s
            WHERE id = %s
        """, ("Alexander Deussen Park", "Lake Houston", spot['id']))
        print(f"   [OK] Updated to:")
        print(f"      Name: Alexander Deussen Park")
        print(f"      Water body: Lake Houston\n")
else:
    print("   Not found\n")

conn.commit()
cur.close()
conn.close()

print("=" * 60)
print("Done!")
