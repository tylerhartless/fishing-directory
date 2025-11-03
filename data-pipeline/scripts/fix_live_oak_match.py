"""
Fix incorrect Live Oak City Lake / Marlin City Lake match
- Remove species votes from Marlin City Lake (ID 613)
- Remove the incorrect address update
"""
import sys
sys.path.insert(0, '..')
import mysql.connector
from config import DB_CONFIG

db_config = {k: v for k, v in DB_CONFIG.items() if k != 'cursorclass'}
conn = mysql.connector.connect(**db_config)
cur = conn.cursor(dictionary=True)

# Check Marlin City Lake (ID 613)
cur.execute("""
    SELECT id, name, address, latitude, longitude, water_body_name, county
    FROM fishing_spots
    WHERE id = 613
""")

spot = cur.fetchone()
print(f"Current state of Marlin City Lake:")
print(f"  ID: {spot['id']}")
print(f"  Name: {spot['name']}")
print(f"  Address: {spot['address']}")
print(f"  County: {spot['county']}")
print(f"  Coords: {spot['latitude']}, {spot['longitude']}")

# Check species votes
cur.execute("""
    SELECT vote_type, vote_count
    FROM spot_votes
    WHERE fishing_spot_id = 613
""")

votes = cur.fetchall()
print(f"\n  Species votes:")
for vote in votes:
    print(f"    {vote['vote_type']}: {vote['vote_count']}")

# The correct Marlin City Lake should be in Falls County, not near Live Oak
# Live Oak is near San Antonio (Bexar County area)
# Marlin is in Falls County (near Waco, ~200+ miles away)

print(f"\n[INFO] This is in {spot['county']} County")
print(f"[INFO] Live Oak City Lake should be near San Antonio (Bexar County area)")
print(f"[INFO] These are clearly different places")

# Remove the incorrect address (it was 18001 Park Drive, Live Oak - wrong place)
print(f"\nRemoving incorrect address from Marlin City Lake...")
cur.execute("""
    UPDATE fishing_spots
    SET address = NULL
    WHERE id = 613
""")

# Remove the incorrect species votes (they were added with vote_count=1)
print(f"Removing incorrect species votes...")
cur.execute("""
    DELETE FROM spot_votes
    WHERE fishing_spot_id = 613 AND vote_count = 1
""")

conn.commit()

print(f"\n[OK] Fixed Marlin City Lake - removed incorrect data")
print(f"\nNote: 'Live Oak City Lake at Main City Park' needs to be added as a new entry with:")
print(f"  - Name: Main City Park")
print(f"  - Water body: Live Oak City Lake")
print(f"  - Address: 18001 Park Drive, Live Oak")
print(f"  - Species: catfish, largemouth_bass, sunfish")

cur.close()
conn.close()
