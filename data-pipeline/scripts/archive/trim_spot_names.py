"""
Trim leading/trailing spaces from spot names in database
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from db_utils import get_connection

conn = get_connection(silent=True)
cursor = conn.cursor()

# Update names with leading/trailing spaces
cursor.execute("UPDATE fishing_spots SET name = TRIM(name) WHERE name != TRIM(name)")
affected = cursor.rowcount
conn.commit()

print(f"Trimmed {affected} spot names in database")

cursor.close()
conn.close()
