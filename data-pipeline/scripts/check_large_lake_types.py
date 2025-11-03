"""Check what spot_type large lakes use"""
import sys
sys.path.insert(0, '..')
import mysql.connector
from config import DB_CONFIG

db_config = {k: v for k, v in DB_CONFIG.items() if k != 'cursorclass'}
conn = mysql.connector.connect(**db_config)
cur = conn.cursor()

# Check what spot_type Livingston and Conroe use
cur.execute("""
    SELECT name, spot_type, water_body_name, data_source
    FROM fishing_spots
    WHERE name LIKE '%Livingston%' OR name LIKE '%Conroe%'
    LIMIT 10
""")

print('Large lake spot types:')
for row in cur.fetchall():
    print(f'  {row[0]:40} | type: {row[1]:15} | water: {row[2]} | source: {row[3]}')

# Also check city park lakes
cur.execute("""
    SELECT name, spot_type, water_body_name, data_source
    FROM fishing_spots
    WHERE data_source LIKE '%City_PDFs%'
    LIMIT 5
""")

print('\nCity PDF spot types:')
for row in cur.fetchall():
    print(f'  {row[0]:40} | type: {row[1]:15} | water: {row[2]} | source: {row[3]}')

cur.close()
conn.close()
