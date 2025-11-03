import sys
sys.path.insert(0, '..')
import mysql.connector
from config import DB_CONFIG

db_config = {k: v for k, v in DB_CONFIG.items() if k != 'cursorclass'}
conn = mysql.connector.connect(**db_config)
cur = conn.cursor(dictionary=True)

# Check for Lake Houston Wilderness Park and Lake Dabney
cur.execute("""
    SELECT id, name, water_body_name, address, latitude, longitude, description, data_source
    FROM fishing_spots
    WHERE name LIKE '%Lake Houston%' OR name LIKE '%Dabney%' OR water_body_name LIKE '%Dabney%'
    ORDER BY name
""")

results = cur.fetchall()
print(f'Found {len(results)} matching entries:\n')

for row in results:
    print(f"ID: {row['id']}")
    print(f"Name: {row['name']}")
    print(f"Water: {row['water_body_name']}")
    print(f"Address: {row['address']}")
    print(f"Coords: {row['latitude']}, {row['longitude']}")
    print(f"Source: {row['data_source']}")
    if row['description']:
        print(f"Description: {row['description'][:100]}...")
    print()

conn.close()
