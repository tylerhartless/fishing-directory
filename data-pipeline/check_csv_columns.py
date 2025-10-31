"""
Quick script to check what columns are in the TPWD CSV
"""
import pandas as pd
import os
from config import RAW_DATA_DIR

csv_path = os.path.join(RAW_DATA_DIR, 'tpwd_boat_ramps.csv')

df = pd.read_csv(csv_path)

print("="*60)
print("CSV COLUMN ANALYSIS")
print("="*60)
print(f"\nTotal rows: {len(df)}")
print(f"\nColumn names found:")
for i, col in enumerate(df.columns, 1):
    print(f"  {i}. {col}")

print("\n" + "="*60)
print("FIRST ROW SAMPLE:")
print("="*60)
for col in df.columns:
    value = df.iloc[0][col]
    print(f"{col}: {value}")

print("\n" + "="*60)
print("SECOND ROW SAMPLE:")
print("="*60)
for col in df.columns:
    value = df.iloc[1][col]
    print(f"{col}: {value}")