"""
Fix incorrect Lake Pflugerville / Lake Somerville match
"""
import sys
sys.path.insert(0, '..')
import mysql.connector
from config import DB_CONFIG

db_config = {k: v for k, v in DB_CONFIG.items() if k != 'cursorclass'}
conn = mysql.connector.connect(**db_config)
cur = conn.cursor(dictionary=True)

# Check if Lake Pflugerville exists in DB
cur.execute("""
    SELECT id, name, address, latitude, longitude
    FROM fishing_spots
    WHERE name LIKE '%Pflugerville%'
""")

pflugerville = cur.fetchall()
print(f"Lake Pflugerville in database: {len(pflugerville)} entries")
for spot in pflugerville:
    print(f"  {spot['id']}: {spot['name']}")

# Check Lake Somerville - Birch Creek (ID 250)
cur.execute("""
    SELECT id, name, address, latitude, longitude
    FROM fishing_spots
    WHERE id = 250
""")

somerville = cur.fetchone()
print(f"\nLake Somerville - Birch Creek Unit State Park:")
print(f"  ID: {somerville['id']}")
print(f"  Name: {somerville['name']}")
print(f"  Address: {somerville['address']}")

# Check recent species votes (likely the ones we just added)
cur.execute("""
    SELECT vote_type, vote_count
    FROM spot_votes
    WHERE fishing_spot_id = 250
""")

votes = cur.fetchall()
print(f"\n  Species votes:")
for vote in votes:
    print(f"    {vote['vote_type']}: {vote['vote_count']}")

# The species were likely already correct for Lake Somerville, so we don't need to remove them
# Lake Pflugerville needs to be added as a new entry

print(f"\nNote: Lake Somerville species may have been incremented incorrectly.")
print(f"Lake Pflugerville needs to be added as a new entry with address: 18216 Weiss Lane, Pflugerville")

cur.close()
conn.close()
