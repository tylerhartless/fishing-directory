"""Remove the Harris County American Legion Park Pond duplicate"""
import sys
sys.path.insert(0, '..')
import mysql.connector
from config import DB_CONFIG

db_config = {k: v for k, v in DB_CONFIG.items() if k != 'cursorclass'}
conn = mysql.connector.connect(**db_config)
cur = conn.cursor(dictionary=True)

print("Removing Harris County American Legion Park Pond duplicate...\n")

# The Harris County entry (ID 3234) is a duplicate of the Fort Bend entry
# Both have the same coordinates and address (4015 Lexington Blvd., Missouri City)
# Missouri City is in Fort Bend County, so the Harris County one is incorrect

harris_id = 3234

print(f"Deleting entry ID {harris_id} (Harris County duplicate)...")

cur.execute("DELETE FROM fishing_spots WHERE id = %s", (harris_id,))
conn.commit()

print(f"[OK] Deleted duplicate entry {harris_id}")
print("\nKeeping entry ID 3280 (Fort Bend County - correct location)")

cur.close()
conn.close()
