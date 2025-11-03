"""
Fix incorrect Barkley Meadows / Jersey Meadows match
- Remove species votes from Jersey Meadows that were incorrectly added
- Remove the address that was incorrectly added
"""
import sys
sys.path.insert(0, '..')
import mysql.connector
from config import DB_CONFIG

db_config = {k: v for k, v in DB_CONFIG.items() if k != 'cursorclass'}
conn = mysql.connector.connect(**db_config)
cur = conn.cursor(dictionary=True)

# Check Jersey Meadows Lake (ID 2640)
cur.execute("""
    SELECT id, name, address, latitude, longitude
    FROM fishing_spots
    WHERE id = 2640
""")

spot = cur.fetchone()
print(f"Current state of Jersey Meadows Lake:")
print(f"  ID: {spot['id']}")
print(f"  Name: {spot['name']}")
print(f"  Address: {spot['address']}")
print(f"  Coords: {spot['latitude']}, {spot['longitude']}")

# Check species votes
cur.execute("""
    SELECT vote_type, vote_count
    FROM spot_votes
    WHERE fishing_spot_id = 2640
""")

votes = cur.fetchall()
print(f"\n  Species votes:")
for vote in votes:
    print(f"    {vote['vote_type']}: {vote['vote_count']}")

# Remove the incorrect address
print(f"\nRemoving incorrect address from Jersey Meadows Lake...")
cur.execute("""
    UPDATE fishing_spots
    SET address = NULL
    WHERE id = 2640
""")

# Remove the species votes (they were added with vote_count=1, so delete if count is 1)
print(f"Removing incorrect species votes...")
cur.execute("""
    DELETE FROM spot_votes
    WHERE fishing_spot_id = 2640 AND vote_count = 1
""")

conn.commit()

print(f"\n[OK] Fixed Jersey Meadows Lake - removed incorrect data")
print(f"\nNote: Barkley Meadows Park is a different location and needs to be added as a new entry.")

cur.close()
conn.close()
