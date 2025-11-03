import sys
sys.path.insert(0, '..')
import mysql.connector
from config import DB_CONFIG

db_config = {k: v for k, v in DB_CONFIG.items() if k != 'cursorclass'}
conn = mysql.connector.connect(**db_config)
cur = conn.cursor()

cur.execute("SELECT COUNT(*) FROM fishing_spots WHERE source_file LIKE '%city%'")
count = cur.fetchone()[0]
print(f'City spots imported: {count}')

if count > 0:
    cur.execute("SELECT name, address, city FROM fishing_spots WHERE source_file LIKE '%city%' LIMIT 5")
    print('\nSample entries:')
    for name, address, city in cur.fetchall():
        print(f'  {name} - {address}, {city}')

conn.close()
