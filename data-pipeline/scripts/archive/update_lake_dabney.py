"""
Update Lake Dabney entry to reflect its location within Lake Houston Wilderness Park
"""
import sys
sys.path.insert(0, '..')
import mysql.connector
from config import DB_CONFIG

db_config = {k: v for k, v in DB_CONFIG.items() if k != 'cursorclass'}
conn = mysql.connector.connect(**db_config)
cur = conn.cursor(dictionary=True)

# Get Lake Dabney
cur.execute("""
    SELECT id, name, water_body_name, description, address
    FROM fishing_spots
    WHERE name = 'Lake Dabney'
""")

lake_dabney = cur.fetchone()

if lake_dabney:
    print(f"Current Lake Dabney entry:")
    print(f"  Name: {lake_dabney['name']}")
    print(f"  Water: {lake_dabney['water_body_name']}")
    print(f"  Address: {lake_dabney['address']}")
    print(f"  Description: {lake_dabney['description'][:100] if lake_dabney['description'] else 'None'}...")
    print()

    # Update the entry
    new_name = "Lake Houston Wilderness Park (Lake Dabney)"

    # Update description to mention the creek access
    current_desc = lake_dabney['description'] or ""

    # Add info about the location and creek access
    location_info = "Located within Lake Houston Wilderness Park. This park features Lake Dabney for fishing, as well as access to Caney Creek which also offers fishing opportunities. "

    # If description already mentions wilderness park, don't duplicate
    if "Lake Houston Wilderness Park" not in current_desc and "Wilderness Park" not in current_desc:
        new_desc = location_info + current_desc
    else:
        new_desc = current_desc

    # Update the record
    cur.execute("""
        UPDATE fishing_spots
        SET name = %s, description = %s
        WHERE id = %s
    """, (new_name, new_desc, lake_dabney['id']))

    conn.commit()

    print("Updated Lake Dabney:")
    print(f"  New name: {new_name}")
    print(f"  Description: {new_desc[:150]}...")
    print()
    print("[OK] Lake Dabney updated successfully")
else:
    print("Lake Dabney not found in database")

conn.close()
