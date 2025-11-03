"""Fix Andrews City Lake to use Lakeside Park as the proper name"""
import sys
sys.path.insert(0, '..')
import mysql.connector
from config import DB_CONFIG

db_config = {k: v for k, v in DB_CONFIG.items() if k != 'cursorclass'}
conn = mysql.connector.connect(**db_config)
cur = conn.cursor(dictionary=True)

print("Fixing Andrews City Lake naming...\n")

# Find Andrews City entries
cur.execute("""
    SELECT id, name, slug, county, water_body_name, description, address
    FROM fishing_spots
    WHERE name LIKE '%Andrews City%'
    AND county = 'Andrews'
""")

andrews_spots = cur.fetchall()

if andrews_spots:
    for spot in andrews_spots:
        print(f"Found: ID {spot['id']}")
        print(f"  Current name: {spot['name']}")
        print(f"  Current water_body: {spot['water_body_name']}")
        print(f"  Description: {spot['description']}")
        print(f"  Address: {spot['address']}")
        print()

        # Update to proper naming
        # Park name: Lakeside Park
        # Water body: Andrews City Lake
        cur.execute("""
            UPDATE fishing_spots
            SET name = %s,
                water_body_name = %s
            WHERE id = %s
        """, ("Lakeside Park", "Andrews City Lake", spot['id']))

        print(f"[OK] Updated to:")
        print(f"  Name: Lakeside Park")
        print(f"  Water body: Andrews City Lake")
        print()

    conn.commit()
    print(f"Updated {len(andrews_spots)} entry/entries")
else:
    print("No Andrews City entries found")

cur.close()
conn.close()
