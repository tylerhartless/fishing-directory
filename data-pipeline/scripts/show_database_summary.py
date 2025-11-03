"""Show database summary"""
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from db_utils import get_connection

conn = get_connection(silent=True)
cursor = conn.cursor(dictionary=True)

print("=" * 70)
print("Texas Fishing Directory - Database Summary")
print("=" * 70)
print()

# By spot type
cursor.execute('''
    SELECT spot_type, COUNT(*) as count
    FROM fishing_spots
    GROUP BY spot_type
    ORDER BY count DESC
''')

results = cursor.fetchall()
total = 0
for row in results:
    print(f"{row['spot_type']:20} {row['count']:5,} spots")
    total += row['count']

print("=" * 70)
print(f"{'TOTAL':20} {total:5,} spots")
print("=" * 70)
print()

# RACA breakdown by river
print("RACA Sites by River:")
print("-" * 70)
cursor.execute('''
    SELECT water_body_name, COUNT(*) as count
    FROM fishing_spots
    WHERE spot_type = 'river_access'
    GROUP BY water_body_name
    ORDER BY count DESC
''')

raca_results = cursor.fetchall()
for row in raca_results:
    print(f"  {row['water_body_name']:30} {row['count']:3} sites")

print("=" * 70)

cursor.close()
conn.close()
