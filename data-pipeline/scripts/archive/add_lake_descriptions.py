"""Add standardized descriptions for different spot types"""
import sys
sys.path.insert(0, '..')
import mysql.connector
from config import DB_CONFIG

db_config = {k: v for k, v in DB_CONFIG.items() if k != 'cursorclass'}
conn = mysql.connector.connect(**db_config)
cur = conn.cursor(dictionary=True)

print("Adding standardized descriptions...\n")

# 1. Large lakes (spot_type = 'lake') - generic description
print("1. Updating large lakes...")
cur.execute("""
    SELECT id, name, description
    FROM fishing_spots
    WHERE spot_type = 'lake'
    AND (description IS NULL OR description = '' OR description = 'null')
""")

large_lakes = cur.fetchall()
print(f"   Found {len(large_lakes)} large lakes without descriptions")

for lake in large_lakes:
    description = f"{lake['name']} is a large reservoir in Texas offering diverse fishing opportunities. Popular among anglers for both bank fishing and boat access."

    cur.execute("""
        UPDATE fishing_spots
        SET description = %s
        WHERE id = %s
    """, (description, lake['id']))
    print(f"   [OK] {lake['name']}")

# 2. Community lakes - mention stocking
print("\n2. Updating community lakes...")
cur.execute("""
    SELECT id, name, description, data_source
    FROM fishing_spots
    WHERE data_source LIKE '%Community%'
    AND (description IS NULL OR description = '' OR description NOT LIKE '%regularly stocked%')
""")

community_lakes = cur.fetchall()
print(f"   Found {len(community_lakes)} community lakes to update")

for lake in community_lakes:
    if lake['description'] and 'regularly stocked' not in lake['description']:
        # Append to existing description
        description = f"{lake['description']} This community fishing lake is regularly stocked by Texas Parks and Wildlife."
    else:
        description = f"{lake['name']} is a community fishing lake regularly stocked by Texas Parks and Wildlife, providing excellent fishing opportunities close to urban areas."

    cur.execute("""
        UPDATE fishing_spots
        SET description = %s
        WHERE id = %s
    """, (description, lake['id']))
    print(f"   [OK] {lake['name']}")

# 3. Neighborhood fishing spots - mention stocking
print("\n3. Updating neighborhood fishing spots...")
cur.execute("""
    SELECT id, name, description, data_source
    FROM fishing_spots
    WHERE data_source LIKE '%Neighborhood%'
    AND (description IS NULL OR description = '' OR description NOT LIKE '%regularly stocked%')
""")

neighborhood_spots = cur.fetchall()
print(f"   Found {len(neighborhood_spots)} neighborhood spots to update")

for spot in neighborhood_spots:
    if spot['description'] and 'regularly stocked' not in spot['description']:
        description = f"{spot['description']} This neighborhood fishing location is regularly stocked by Texas Parks and Wildlife."
    else:
        description = f"{spot['name']} is a neighborhood fishing location regularly stocked by Texas Parks and Wildlife, offering convenient fishing access for local communities."

    cur.execute("""
        UPDATE fishing_spots
        SET description = %s
        WHERE id = %s
    """, (description, spot['id']))
    print(f"   [OK] {spot['name']}")

conn.commit()
cur.close()
conn.close()

print("\n" + "="*60)
print("Done!")
print("="*60)
