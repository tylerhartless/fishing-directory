"""Clean up and shorten descriptions to fit in tiles"""
import sys
sys.path.insert(0, '..')
import mysql.connector
from config import DB_CONFIG
import re

db_config = {k: v for k, v in DB_CONFIG.items() if k != 'cursorclass'}
conn = mysql.connector.connect(**db_config)
cur = conn.cursor(dictionary=True)

print("Cleaning up descriptions...\n")

# 1. Remove target species mentions from all descriptions
print("1. Removing target species mentions...")
cur.execute("""
    SELECT id, name, description
    FROM fishing_spots
    WHERE description IS NOT NULL
    AND description != ''
    AND description != 'null'
""")

all_spots = cur.fetchall()
species_patterns = [
    r'Target species include:.*?(?=\.|$)',
    r'Species:.*?(?=\.|$)',
    r'Fish species:.*?(?=\.|$)',
    r'Popular fish:.*?(?=\.|$)',
    r'\(.*?(?:Bass|Catfish|Sunfish|Crappie|Trout|Carp|Gar).*?\)',
]

species_cleaned = 0
for spot in all_spots:
    original_desc = spot['description']
    cleaned_desc = original_desc

    # Apply all species removal patterns
    for pattern in species_patterns:
        cleaned_desc = re.sub(pattern, '', cleaned_desc, flags=re.IGNORECASE)

    # Clean up extra whitespace and periods
    cleaned_desc = re.sub(r'\s+', ' ', cleaned_desc)
    cleaned_desc = re.sub(r'\.\s*\.', '.', cleaned_desc)
    cleaned_desc = cleaned_desc.strip()

    if cleaned_desc != original_desc:
        cur.execute("""
            UPDATE fishing_spots
            SET description = %s
            WHERE id = %s
        """, (cleaned_desc, spot['id']))
        species_cleaned += 1

print(f"   Cleaned species mentions from {species_cleaned} descriptions")

# 2. Fix specific descriptions with old names
print("\n2. Fixing descriptions with old combined names...")

# Alexander Deussen Park
cur.execute("""
    SELECT id, name, description
    FROM fishing_spots
    WHERE name LIKE '%Alexander Deussen%'
    OR name LIKE '%Deussen%'
""")

deussen_spots = cur.fetchall()
for spot in deussen_spots:
    if spot['description'] and 'Alexander Deussen Park on Lake Houston' in spot['description']:
        # Replace the old combined name with just the park name
        new_desc = spot['description'].replace(
            'Alexander Deussen Park on Lake Houston',
            'Alexander Deussen Park'
        )
        cur.execute("""
            UPDATE fishing_spots
            SET description = %s
            WHERE id = %s
        """, (new_desc, spot['id']))
        print(f"   [OK] Fixed: {spot['name']}")

# 3. Shorten verbose descriptions for all spot types
print("\n3. Shortening descriptions to fit in tiles...")

# State Parks - keep it simple about license
cur.execute("""
    SELECT id, name, description
    FROM fishing_spots
    WHERE spot_type = 'state_park'
    AND description IS NOT NULL
""")

state_parks = cur.fetchall()
for park in state_parks:
    # Short version emphasizing no license required
    short_desc = f"State park with fishing access. No fishing license required."

    cur.execute("""
        UPDATE fishing_spots
        SET description = %s
        WHERE id = %s
    """, (short_desc, park['id']))

print(f"   Updated {len(state_parks)} state parks")

# Community lakes - brief mention of stocking
cur.execute("""
    SELECT id, name, description
    FROM fishing_spots
    WHERE data_source LIKE '%Community%'
""")

community_lakes = cur.fetchall()
for lake in community_lakes:
    short_desc = "Community fishing lake regularly stocked by TPWD."

    cur.execute("""
        UPDATE fishing_spots
        SET description = %s
        WHERE id = %s
    """, (short_desc, lake['id']))

print(f"   Updated {len(community_lakes)} community lakes")

# Neighborhood fishing spots - brief mention of stocking
cur.execute("""
    SELECT id, name, description
    FROM fishing_spots
    WHERE data_source LIKE '%Neighborhood%'
""")

neighborhood_spots = cur.fetchall()
for spot in neighborhood_spots:
    short_desc = "Neighborhood fishing spot regularly stocked by TPWD."

    cur.execute("""
        UPDATE fishing_spots
        SET description = %s
        WHERE id = %s
    """, (short_desc, spot['id']))

print(f"   Updated {len(neighborhood_spots)} neighborhood spots")

# Large lakes - very brief
cur.execute("""
    SELECT id, name, description
    FROM fishing_spots
    WHERE spot_type = 'lake'
""")

large_lakes = cur.fetchall()
for lake in large_lakes:
    short_desc = "Large reservoir with diverse fishing opportunities."

    cur.execute("""
        UPDATE fishing_spots
        SET description = %s
        WHERE id = %s
    """, (short_desc, lake['id']))

print(f"   Updated {len(large_lakes)} large lakes")

# Boat ramps - simple description
cur.execute("""
    SELECT id, name, description
    FROM fishing_spots
    WHERE spot_type = 'boat_ramp'
""")

boat_ramps = cur.fetchall()
for ramp in boat_ramps:
    short_desc = "Public boat ramp with water access."

    cur.execute("""
        UPDATE fishing_spots
        SET description = %s
        WHERE id = %s
    """, (short_desc, ramp['id']))

print(f"   Updated {len(boat_ramps)} boat ramps")

# Other fishing access types - generic short description
cur.execute("""
    SELECT id, name, description, spot_type
    FROM fishing_spots
    WHERE spot_type IN ('bank_fishing', 'pier', 'wade_fishing', 'kayak_launch', 'fishing_pier', 'public_water', 'river_access')
""")

other_spots = cur.fetchall()
for spot in other_spots:
    spot_type_map = {
        'bank_fishing': "Bank fishing access.",
        'pier': "Fishing pier with water access.",
        'wade_fishing': "Wade fishing access point.",
        'kayak_launch': "Kayak launch with fishing access.",
        'fishing_pier': "Public fishing pier.",
        'public_water': "Public water access for fishing.",
        'river_access': "River access point for fishing."
    }

    short_desc = spot_type_map.get(spot['spot_type'], "Public fishing access.")

    cur.execute("""
        UPDATE fishing_spots
        SET description = %s
        WHERE id = %s
    """, (short_desc, spot['id']))

print(f"   Updated {len(other_spots)} other fishing access spots")

conn.commit()
cur.close()
conn.close()

print("\n" + "="*60)
print("Done! All descriptions cleaned and shortened.")
print("="*60)
