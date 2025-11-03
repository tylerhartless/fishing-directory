"""Run migration 004 - Add lake and public_water spot types"""
import sys
sys.path.insert(0, '..')
import mysql.connector
from config import DB_CONFIG

db_config = {k: v for k, v in DB_CONFIG.items() if k != 'cursorclass'}
conn = mysql.connector.connect(**db_config)
cur = conn.cursor()

print("Running migration 004...")
print("Adding 'lake' and 'public_water' to spot_type enum...")

try:
    cur.execute("""
        ALTER TABLE fishing_spots
        MODIFY COLUMN spot_type ENUM(
            'boat_ramp',
            'bank_fishing',
            'pier',
            'wade_fishing',
            'kayak_launch',
            'fishing_pier',
            'state_park',
            'lake',
            'public_water',
            'river_access'
        ) NOT NULL
    """)
    conn.commit()
    print("[OK] Migration completed successfully")
except Exception as e:
    print(f"[ERROR] Migration failed: {e}")
    conn.rollback()

cur.close()
conn.close()
