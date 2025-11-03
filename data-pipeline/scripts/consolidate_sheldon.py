"""
Consolidate all Sheldon Lake entries into one main listing:
Sheldon Lake State Park and Environmental Learning Center

Keep:
- ID 3254: Sheldon Lake State Park and Environmental Learning Center (as PARENT)

Make children:
- ID 2650, 2651, 2652: Children's ponds (already named correctly)
- ID 2649: Sheldon Prairie Pond
- ID 2648: Sheldon (duplicate)

Delete:
- ID 3171: Lake Sheldon (doesn't exist, it's just Sheldon Lake)
- ID 800: Sheldon Lake State Park (duplicate of 3254)

Keep separate (boat ramp):
- ID 799: Sheldon Reservoir boat ramp
"""

import mysql.connector
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.append('..')
from config import DB_CONFIG

print("="*70)
print("CONSOLIDATING SHELDON LAKE ENTRIES")
print("="*70)
print()

conn = mysql.connector.connect(**DB_CONFIG)
cur = conn.cursor(dictionary=True)

# Set the main entry as parent
PARENT_ID = 3254
CHILD_IDS = [2650, 2651, 2652, 2649, 2648]
DELETE_IDS = [3171, 800]

print("Main entry (will be parent):")
cur.execute("SELECT id, name FROM fishing_spots WHERE id = %s", (PARENT_ID,))
parent = cur.fetchone()
print(f"  ID {parent['id']}: {parent['name']}")
print()

# Set as parent
cur.execute("""
    UPDATE fishing_spots
    SET is_parent = TRUE
    WHERE id = %s
""", (PARENT_ID,))
print("✓ Set as parent")
print()

# Link children
print(f"Linking {len(CHILD_IDS)} children:")
for child_id in CHILD_IDS:
    cur.execute("SELECT id, name FROM fishing_spots WHERE id = %s", (child_id,))
    child = cur.fetchone()
    print(f"  ID {child['id']}: {child['name']}")

    cur.execute("""
        UPDATE fishing_spots
        SET parent_spot_id = %s, is_parent = FALSE
        WHERE id = %s
    """, (PARENT_ID, child_id))

print("✓ Linked children")
print()

# Delete duplicates
print(f"Deleting {len(DELETE_IDS)} duplicates:")
for del_id in DELETE_IDS:
    cur.execute("SELECT id, name FROM fishing_spots WHERE id = %s", (del_id,))
    dup = cur.fetchone()
    print(f"  ID {dup['id']}: {dup['name']}")

    cur.execute("DELETE FROM fishing_spots WHERE id = %s", (del_id,))

print("✓ Deleted duplicates")
print()

conn.commit()

# Verify
print("="*70)
print("VERIFICATION")
print("="*70)
print()

cur.execute("""
    SELECT id, name, parent_spot_id, is_parent
    FROM fishing_spots
    WHERE name LIKE '%Sheldon%'
    ORDER BY CASE WHEN is_parent THEN 0 ELSE 1 END, name
""")

remaining = cur.fetchall()
print(f"Remaining Sheldon entries: {len(remaining)}\n")

for spot in remaining:
    parent_info = ''
    if spot['parent_spot_id']:
        parent_info = f' (child of {spot["parent_spot_id"]})'
    elif spot['is_parent']:
        parent_info = ' ⭐ PARENT'

    print(f"ID {spot['id']}: {spot['name']}{parent_info}")

conn.close()

print()
print("="*70)
print("COMPLETE")
print("="*70)
print()
print("✅ Consolidated all Sheldon Lake entries")
print("✅ Main listing: Sheldon Lake State Park and Environmental Learning Center")
print("✅ 5 children hidden from main search")
print("✅ 2 duplicates removed")
print("✅ Boat ramp kept separate")
