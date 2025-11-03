"""Count public_water spots needing OSM enrichment"""
import sys
sys.path.insert(0, '..')
import mysql.connector
from config import DB_CONFIG

db_config = {k: v for k, v in DB_CONFIG.items() if k != 'cursorclass'}
conn = mysql.connector.connect(**db_config)
cur = conn.cursor(dictionary=True)

print("Checking public_water spots...\n")

# Total count
cur.execute("SELECT COUNT(*) as count FROM fishing_spots WHERE spot_type = 'public_water'")
total = cur.fetchone()['count']

# Count with/without amenities
cur.execute("SELECT COUNT(*) as count FROM fishing_spots WHERE spot_type = 'public_water' AND amenities IS NOT NULL")
with_amenities = cur.fetchone()['count']

# Count with/without addresses
cur.execute("SELECT COUNT(*) as count FROM fishing_spots WHERE spot_type = 'public_water' AND address IS NOT NULL AND address != ''")
with_address = cur.fetchone()['count']

print(f"Total public_water spots: {total}")
print(f"With amenities data: {with_amenities}")
print(f"With address data: {with_address}")
print(f"\nNeed enrichment: {total - with_amenities} (no amenities)")

cur.close()
conn.close()
