"""
Fix "Multiple Counties County" to just "Multiple Counties"
"""

import mysql.connector
import sys
import io

# Fix Windows console encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

sys.path.append('..')
from config import DB_CONFIG

def fix_counties():
    conn = mysql.connector.connect(**DB_CONFIG)
    cur = conn.cursor(dictionary=True)

    print("=== Fixing 'Multiple Counties County' ===\n")

    # Find and fix spots
    cur.execute("""
        SELECT id, name, county, spot_type
        FROM fishing_spots
        WHERE county LIKE '%Multiple Counties%'
        ORDER BY spot_type, name
    """)
    spots = cur.fetchall()

    print(f"Found {len(spots)} spots with 'Multiple Counties County'\n")

    for spot in spots:
        print(f"ID {spot['id']}: {spot['name']} ({spot['spot_type']})")
        print(f"  Before: '{spot['county']}'")
        print(f"  After: 'Multiple Counties'")

        cur.execute("""
            UPDATE fishing_spots
            SET county = 'Multiple Counties'
            WHERE id = %s
        """, (spot['id'],))

        print("  ✓ Fixed\n")

    conn.commit()

    print(f"{'='*60}")
    print(f"✓ Fixed {len(spots)} spots")

    conn.close()

if __name__ == "__main__":
    fix_counties()
