"""Check what spot_type value is causing the migration to fail"""
import sys
sys.path.insert(0, '..')
import mysql.connector
from config import DB_CONFIG

db_config = {k: v for k, v in DB_CONFIG.items() if k != 'cursorclass'}
conn = mysql.connector.connect(**db_config)
cur = conn.cursor(dictionary=True)

# Check what's in row 3204
cur.execute("SELECT id, name, spot_type FROM fishing_spots WHERE id = 3204")
row = cur.fetchone()

if row:
    print(f"Row 3204:")
    print(f"  ID: {row['id']}")
    print(f"  Name: {row['name']}")
    print(f"  spot_type: '{row['spot_type']}'")
else:
    print("Row 3204 not found")

# Check all unique spot_type values
cur.execute("SELECT DISTINCT spot_type, COUNT(*) as count FROM fishing_spots GROUP BY spot_type")
print("\nAll current spot_type values:")
for row in cur.fetchall():
    print(f"  {row['spot_type']:20} : {row['count']} rows")

cur.close()
conn.close()
