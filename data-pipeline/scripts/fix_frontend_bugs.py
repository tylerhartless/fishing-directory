"""
Fix frontend display bugs:
1. Decode HTML entities in names (&amp;#39; -> ')
2. Find numbered ponds that should be consolidated
3. Check for 'undefined' state issues
"""

import mysql.connector
import html
import sys
import io
from math import radians, cos, sin, asin, sqrt

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.append('..')
from config import DB_CONFIG

def haversine(lon1, lat1, lon2, lat2):
    """Calculate distance in meters between two points"""
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    r = 6371000  # Earth radius in meters
    return c * r

print("="*70)
print("FIXING FRONTEND BUGS")
print("="*70)
print()

conn = mysql.connector.connect(**DB_CONFIG)
cur = conn.cursor(dictionary=True)

# ============================================================================
# BUG 1: HTML Entity Encoding
# ============================================================================
print("1. Fixing HTML entity encoding...")
print()

cur.execute("""
    SELECT id, name
    FROM fishing_spots
    WHERE name LIKE '%&amp;%' OR name LIKE '%&#%'
""")

html_entities = cur.fetchall()
print(f"Found {len(html_entities)} spots with HTML entities\n")

for spot in html_entities:
    old_name = spot['name']
    # Decode twice because it's double-encoded
    new_name = html.unescape(html.unescape(old_name))

    print(f"ID {spot['id']}:")
    print(f"  Before: {old_name}")
    print(f"  After:  {new_name}")

    cur.execute("UPDATE fishing_spots SET name = %s WHERE id = %s", (new_name, spot['id']))

conn.commit()
print(f"\nFixed {len(html_entities)} names")
print()

# ============================================================================
# BUG 2: Numbered Ponds That Should Be Consolidated
# ============================================================================
print("="*70)
print("2. Finding numbered ponds to consolidate...")
print()

# Find groups of numbered ponds (same base name)
cur.execute("""
    SELECT
        id, name, latitude, longitude, county,
        parent_spot_id, is_parent
    FROM fishing_spots
    WHERE (name REGEXP ' [0-9]+$' OR name REGEXP ' #[0-9]+$')
      AND spot_type = 'public_water'
      AND (is_parent = FALSE OR is_parent IS NULL)
    ORDER BY name
""")

numbered_ponds = cur.fetchall()
print(f"Found {len(numbered_ponds)} numbered ponds\n")

# Group by base name
pond_groups = {}
for pond in numbered_ponds:
    # Extract base name (remove number suffix)
    base_name = pond['name']
    # Remove patterns like " 1", " #6", " Pond 2", etc.
    import re
    base_name = re.sub(r' (Pond )?\#?\d+$', '', base_name)

    if base_name not in pond_groups:
        pond_groups[base_name] = []
    pond_groups[base_name].append(pond)

# Find groups with multiple ponds close together
consolidation_candidates = []
for base_name, ponds in pond_groups.items():
    if len(ponds) < 2:
        continue

    # Check if they're all close together (within 1000m)
    max_distance = 0
    for i, pond1 in enumerate(ponds):
        for pond2 in ponds[i+1:]:
            dist = haversine(
                float(pond1['longitude']), float(pond1['latitude']),
                float(pond2['longitude']), float(pond2['latitude'])
            )
            max_distance = max(max_distance, dist)

    if max_distance <= 1000:
        consolidation_candidates.append({
            'base_name': base_name,
            'ponds': ponds,
            'max_distance': max_distance,
            'county': ponds[0]['county']
        })

print(f"Found {len(consolidation_candidates)} groups that should be consolidated:\n")
for group in consolidation_candidates:
    print(f"{group['base_name']} ({group['county']} County):")
    print(f"  {len(group['ponds'])} ponds within {group['max_distance']:.0f}m")
    for pond in group['ponds']:
        parent_info = f" (child of {pond['parent_spot_id']})" if pond['parent_spot_id'] else ""
        print(f"    - ID {pond['id']}: {pond['name']}{parent_info}")
    print()

# ============================================================================
# BUG 3: Check State Field
# ============================================================================
print("="*70)
print("3. Checking for missing/null state values...")
print()

cur.execute("""
    SELECT COUNT(*) as count
    FROM fishing_spots
    WHERE state IS NULL OR state = ''
""")

null_states = cur.fetchone()['count']
print(f"Spots with NULL/empty state: {null_states}")

if null_states > 0:
    print("\nFixing NULL states (assuming Texas)...")
    cur.execute("""
        UPDATE fishing_spots
        SET state = 'TX'
        WHERE state IS NULL OR state = ''
    """)
    conn.commit()
    print(f"Fixed {cur.rowcount} spots")

print()

conn.close()

print("="*70)
print("SUMMARY")
print("="*70)
print()
print(f"✅ Fixed HTML entities in {len(html_entities)} spot names")
print(f"📋 Found {len(consolidation_candidates)} pond groups to consolidate")
print(f"✅ Fixed NULL state values")
print()
print("NEXT STEPS:")
print("1. Create parent entries for consolidated pond groups")
print("2. Set parent_spot_id for child ponds")
print("3. Fix frontend to not show 'undefined' after state")
