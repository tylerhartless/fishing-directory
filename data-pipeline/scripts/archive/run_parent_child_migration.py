"""
Run parent-child relationship migration
"""

import mysql.connector
import sys
import io

# Fix Windows console encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

sys.path.append('..')
from config import DB_CONFIG

def run_migration():
    conn = mysql.connector.connect(**DB_CONFIG)
    cur = conn.cursor()

    print("=== Running Parent-Child Migration ===\n")

    # Step 1: Add parent_spot_id column
    print("1. Adding parent_spot_id column...")
    try:
        cur.execute("""
            ALTER TABLE fishing_spots
            ADD COLUMN parent_spot_id INT NULL AFTER id
        """)
        print("   ✓ Added parent_spot_id\n")
    except mysql.connector.Error as e:
        if "Duplicate column" in str(e):
            print("   - Column already exists\n")
        else:
            raise

    # Step 2: Add is_parent column
    print("2. Adding is_parent column...")
    try:
        cur.execute("""
            ALTER TABLE fishing_spots
            ADD COLUMN is_parent BOOLEAN DEFAULT FALSE AFTER parent_spot_id
        """)
        print("   ✓ Added is_parent\n")
    except mysql.connector.Error as e:
        if "Duplicate column" in str(e):
            print("   - Column already exists\n")
        else:
            raise

    # Step 3: Add index
    print("3. Adding index for parent lookups...")
    try:
        cur.execute("""
            ALTER TABLE fishing_spots
            ADD INDEX idx_parent_spot (parent_spot_id)
        """)
        print("   ✓ Added index\n")
    except mysql.connector.Error as e:
        if "Duplicate key" in str(e):
            print("   - Index already exists\n")
        else:
            raise

    # Step 4: Add foreign key
    print("4. Adding foreign key constraint...")
    try:
        cur.execute("""
            ALTER TABLE fishing_spots
            ADD CONSTRAINT fk_parent_spot
            FOREIGN KEY (parent_spot_id) REFERENCES fishing_spots(id)
            ON DELETE CASCADE
        """)
        print("   ✓ Added foreign key\n")
    except mysql.connector.Error as e:
        if "Duplicate foreign key" in str(e) or "fk_parent_spot" in str(e):
            print("   - Foreign key already exists\n")
        else:
            raise

    # Step 5: Set Jesse H. Jones Park as parent with children
    print("5. Setting up Jesse H. Jones Park parent-child relationship...")

    # Make Jesse H. Jones Park the parent
    cur.execute("UPDATE fishing_spots SET is_parent = TRUE WHERE id = 3290")
    print("   ✓ Set Jesse H. Jones Park (ID 3290) as parent")

    # Make Salad Bowl Pond and Jones Youth Lake children
    cur.execute("""
        UPDATE fishing_spots
        SET parent_spot_id = 3290, is_parent = FALSE
        WHERE id IN (2641, 2647)
    """)
    print("   ✓ Set Salad Bowl Pond (2647) and Jones Youth Lake (2641) as children\n")

    conn.commit()

    # Verify the setup
    print("6. Verifying setup...")
    cur.execute("""
        SELECT id, name, parent_spot_id, is_parent
        FROM fishing_spots
        WHERE id IN (3290, 2641, 2647)
        ORDER BY id
    """)
    spots = cur.fetchall()

    print("\n   Parent-Child Structure:")
    for spot in spots:
        if spot[3]:  # is_parent
            print(f"   📂 ID {spot[0]}: {spot[1]} (PARENT)")
        else:
            print(f"   └─ ID {spot[0]}: {spot[1]} (child of {spot[2]})")

    print(f"\n{'='*60}")
    print("✓ Migration completed successfully!")
    print("\nNext steps:")
    print("- Update API to filter by is_parent=TRUE or parent_spot_id IS NULL")
    print("- Update frontend to display child spots on detail pages")

    conn.close()

if __name__ == "__main__":
    run_migration()
