"""Show enrichment time estimates by spot type"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from db_utils import get_connection

conn = get_connection(silent=True)
cursor = conn.cursor(dictionary=True)
cursor.execute('SELECT spot_type, COUNT(*) as count FROM fishing_spots GROUP BY spot_type ORDER BY count DESC')
results = cursor.fetchall()

print('Spots by type:')
print('-'*60)
total = 0
for r in results:
    time_min = r['count'] * 0.6 / 60
    print(f'{r["spot_type"]:20} {r["count"]:5} spots  ({time_min:5.1f} min)')
    total += r['count']

print('-'*60)
total_time = total * 0.6 / 60
print(f'{"TOTAL":20} {total:5} spots  ({total_time:5.1f} min)')
print()
print(f'Estimated total time: {total_time:.0f} minutes ({total_time/60:.1f} hours)')
