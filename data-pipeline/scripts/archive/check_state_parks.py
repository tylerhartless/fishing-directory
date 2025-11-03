import sys
sys.path.insert(0, '..')
import mysql.connector
from config import DB_CONFIG

db_config = {k: v for k, v in DB_CONFIG.items() if k != 'cursorclass'}
conn = mysql.connector.connect(**db_config)
cur = conn.cursor(dictionary=True)

# Check state parks
cur.execute("""
    SELECT name, water_body_name, address, latitude, longitude, data_source
    FROM fishing_spots
    WHERE data_source LIKE '%state_park%'
    ORDER BY name
""")

parks = cur.fetchall()
print(f'Total state parks: {len(parks)}\n')

# Look for specific problematic ones
problem_parks = ['Brazos Bend', 'Abilene', 'Daingerfield', 'Cleburne', 'Lake Houston Wilderness']

for park in parks:
    for problem in problem_parks:
        if problem.lower() in park['name'].lower():
            print(f"Name: {park['name']}")
            print(f"  Water: {park['water_body_name']}")
            print(f"  Address: {park['address']}")
            print(f"  Coords: {park['latitude']}, {park['longitude']}")
            print(f"  Source: {park['data_source']}\n")

conn.close()
