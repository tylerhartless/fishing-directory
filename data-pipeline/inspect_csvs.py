"""
Quick CSV Inspector

Shows you the columns and sample data from your CSVs
so you can adjust the adapter column mappings.
"""

import pandas as pd
import sys

def inspect_csv(filepath):
    """Inspect a CSV file and show useful info"""
    print(f"\n{'='*70}")
    print(f"Inspecting: {filepath}")
    print(f"{'='*70}\n")

    try:
        df = pd.read_csv(filepath)

        print(f"Total rows: {len(df)}")
        print(f"\nColumns ({len(df.columns)}):")
        for i, col in enumerate(df.columns, 1):
            print(f"  {i:2d}. {col}")

        print(f"\nFirst 3 rows:")
        print(df.head(3).to_string())

        print(f"\nColumn types:")
        print(df.dtypes)

        # Look for fishing-related data
        print(f"\nSearching for fishing-related columns...")
        fishing_cols = [col for col in df.columns if 'fish' in col.lower() or 'activity' in col.lower()]
        if fishing_cols:
            print(f"Found: {fishing_cols}")
            for col in fishing_cols:
                print(f"\n{col} unique values:")
                print(df[col].value_counts().head(10))

        # Look for amenity-related data
        print(f"\nSearching for amenity/facility columns...")
        amenity_cols = [col for col in df.columns if any(word in col.lower() for word in ['amenity', 'facility', 'restroom', 'type'])]
        if amenity_cols:
            print(f"Found: {amenity_cols}")
            for col in amenity_cols:
                print(f"\n{col} unique values:")
                print(df[col].value_counts().head(10))

    except Exception as e:
        print(f"❌ Error reading file: {e}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python inspect_csvs.py <path_to_csv>")
        print("\nExample:")
        print("  python inspect_csvs.py ../raw-data/point_of_interest.csv")
        print("  python inspect_csvs.py ../raw-data/public_building_structure.csv")
        sys.exit(1)

    for filepath in sys.argv[1:]:
        inspect_csv(filepath)
