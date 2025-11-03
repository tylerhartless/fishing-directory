"""
Consolidate numbered ponds within 1000m into parent entries
"""

import mysql.connector
import sys
import io
from math import radians, cos, sin, asin, sqrt
import re

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.append('..')
from config import DB_CONFIG

def haversine(lon1, lat1, lon2, lat2):
    """Calculate distance in meters"""
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    return c * 6371000

# Pond groups to consolidate (from previous analysis)
CONSOLIDATION_GROUPS = [
    {'base': 'Bates Allen Park', 'county': 'Fort Bend', 'ids': [2548, 2549]},
    {'base': 'Davidson Creek', 'county': 'Burleson', 'ids': [2329, 2330]},
    {'base': 'Engeling WMA', 'county': 'Anderson', 'ids': [2252, 2253]},
    {'base': 'Evergreen Pond', 'county': 'Harris', 'ids': [2630, 2631, 2632]},
    {'base': 'Fischer Park', 'county': 'Comal', 'ids': [2418, 2419]},
    {'base': 'Green-Dickson Municipal Park', 'county': 'Lavaca', 'ids': [2749, 2750]},
    {'base': 'Greenbelt Stilling Basin', 'county': 'Donley', 'ids': [2526, 2527]},
    {'base': 'Hackberry Park', 'county': 'Harris', 'ids': [2633, 2634, 2635, 2636, 2637]},
    {'base': 'Hemphill County Pond', 'county': 'Hemphill', 'ids': [2668, 2669, 2670]},
    {'base': 'Hubbard City Pond', 'county': 'Hill', 'ids': [2686, 2687, 2688, 2689]},
    {'base': 'Jones Lake', 'county': 'Montgomery', 'ids': [2807, 2808, 2809]},
    {'base': 'Little Chocolate Bayou Park', 'county': 'Calhoun', 'ids': [2336, 2337]},
    {'base': 'Matador Pond', 'county': 'Cottle', 'ids': [2426, 2427]},
    {'base': 'Mexia State School Pond', 'county': 'Limestone', 'ids': [2758, 2759]},
    {'base': 'Pearland Parkway Pond', 'county': 'Brazoria', 'ids': [2313, 2314]},
    {'base': 'Pedigo Park', 'county': 'Polk', 'ids': [2827, 2828]},
    {'base': 'Southwest Nature Preserve', 'county': 'Tarrant', 'ids': [2899, 2900]},
    {'base': 'Wolfe City Pond', 'county': 'Hunt', 'ids': [2706, 2707]},
]

print("="*70)
print("CONSOLIDATING NUMBERED PONDS")
print("="*70)
print()

conn = mysql.connector.connect(**DB_CONFIG)
cur = conn.cursor(dictionary=True)

parents_created = 0
children_linked = 0

for group in CONSOLIDATION_GROUPS:
    base_name = group['base']
    county = group['county']
    child_ids = group['ids']

    print(f"📍 {base_name} ({county} County)")
    print(f"   Consolidating {len(child_ids)} ponds...")

    # Get details of first child (for coordinates)
    cur.execute("""
        SELECT latitude, longitude, state, water_body_name, description, amenities
        FROM fishing_spots
        WHERE id = %s
    """, (child_ids[0],))

    first_child = cur.fetchone()

    # Create parent entry
    parent_name = base_name
    slug = f"{base_name.lower().replace(' ', '-')}-{county.lower()}"

    # Get all child water body names
    cur.execute("""
        SELECT water_body_name
        FROM fishing_spots
        WHERE id IN ({})
    """.format(','.join(['%s'] * len(child_ids))), child_ids)

    child_water_bodies = [row['water_body_name'] for row in cur.fetchall()]
    unique_water_bodies = list(set(child_water_bodies))

    # Use parent name as water body if multiple different ones
    water_body = unique_water_bodies[0] if len(unique_water_bodies) == 1 else base_name

    description = f"Public water access with {len(child_ids)} fishing areas."

    # Insert parent
    cur.execute("""
        INSERT INTO fishing_spots
        (name, slug, spot_type, county, state, latitude, longitude,
         water_body_name, description, data_source, is_parent, created_at, updated_at)
        VALUES (%s, %s, 'public_water', %s, %s, %s, %s, %s, %s, 'Manual_Consolidation', TRUE, NOW(), NOW())
    """, (parent_name, slug, county, first_child['state'],
          first_child['latitude'], first_child['longitude'],
          water_body, description))

    parent_id = cur.lastrowid
    print(f"   ✓ Created parent (ID {parent_id})")

    # Link children to parent
    for child_id in child_ids:
        cur.execute("""
            UPDATE fishing_spots
            SET parent_spot_id = %s, is_parent = FALSE
            WHERE id = %s
        """, (parent_id, child_id))
        children_linked += 1

    print(f"   ✓ Linked {len(child_ids)} children")
    print()

    parents_created += 1

conn.commit()
conn.close()

print("="*70)
print("CONSOLIDATION COMPLETE")
print("="*70)
print()
print(f"✅ Created {parents_created} parent entries")
print(f"✅ Linked {children_linked} child ponds")
print()
print("The frontend will now show only parent entries,")
print("hiding the individual numbered ponds from search results.")
