import sys
sys.path.insert(0, '..')
import mysql.connector
from config import DB_CONFIG

db_config = {k: v for k, v in DB_CONFIG.items() if k != 'cursorclass'}
conn = mysql.connector.connect(**db_config)
cur = conn.cursor()

cur.execute('DELETE FROM spot_votes WHERE fishing_spot_id = 250 AND vote_count = 1')
conn.commit()
print(f'Removed {cur.rowcount} incorrect votes from Lake Somerville')
conn.close()
