"""
ETL Script: Process TPWD Boat Ramps Data

Data Source: https://tpwd.texas.gov/gis/resources/boat-access.phtml

Instructions:
1. Download the boat ramps CSV from TPWD website
2. Save it as: ../raw-data/tpwd_boat_ramps.csv
3. Run this script: python process_boat_ramps.py
"""

import pandas as pd
import json
from slugify import slugify
from db_utils import bulk_insert, check_duplicate_slug
from config import RAW_DATA_DIR, PROCESSED_DATA_DIR
import os

def clean_amenities(row):
    """
    Extract amenities from CSV columns and convert to JSON

    Args:
        row: DataFrame row

    Returns:
        str: JSON string of amenities
    """
    amenities = {
        'parking': row.get('PARKING', 'N').upper() == 'Y',
        'restrooms': row.get('RESTROOMS', 'N').upper() == 'Y',
        'lighting': row.get('LIGHTING', 'N').upper() == 'Y',
        'fish_cleaning': row.get('FISH_CLEAN', 'N').upper() == 'Y',
        'boat_trailer_parking': True,  # Assumed for boat ramps
        'camping': row.get('CAMPING', 'N').upper() == 'Y',
    }

    return json.dumps(amenities)

def generate_unique_slug(name, county, base_slug=None):
    """
    Generate a unique slug, handling duplicates

    Args:
        name (str): Spot name
        county (str): County name
        base_slug (str): Optional pre-generated slug

    Returns:
        str: Unique slug
    """
    if not base_slug:
        base_slug = slugify(f"{name}-{county}")

    slug = base_slug
    counter = 1

    while check_duplicate_slug(slug):
        slug = f"{base_slug}-{counter}"
        counter += 1

    return slug

def process_boat_ramps(csv_filename='tpwd_boat_ramps.csv'):
    """
    Main processing function for boat ramps data

    Args:
        csv_filename (str): Name of CSV file in raw-data directory
    """
    csv_path = os.path.join(RAW_DATA_DIR, csv_filename)

    if not os.path.exists(csv_path):
        print(f"✗ File not found: {csv_path}")
        print(f"Please download TPWD boat ramps data and save as: {csv_path}")
        return

    print(f"Reading data from: {csv_path}")
    df = pd.read_csv(csv_path)

    print(f"Found {len(df)} boat ramps to process")

    # Expected columns (adjust based on actual TPWD CSV format):
    # RAMP_NAME, COUNTY, WATERBODY, LATITUDE, LONGITUDE, PARKING, RESTROOMS, etc.

    data_to_insert = []

    for idx, row in df.iterrows():
        # Extract name from TPWAID (e.g., 'anderson001' -> 'Anderson 001')
        tpwaid = str(row.get('TPWAID', f'unknown{idx}'))

        # Parse county from TPWAID (part before number)
        import re
        county_match = re.match(r'([a-zA-Z]+)', tpwaid)
        county = county_match.group(1).title() if county_match else 'Unknown'

        # Get water body and access type
        water_body = row.get('AccessTypeDescription', 'Local Waters')
        access_type = row.get('AccessType', 'Unknown')

        # Create a readable name with TPWAID for uniqueness
        name = f"{water_body} - {county} County Access ({tpwaid})"

        # Generate unique slug using TPWAID to ensure uniqueness
        slug = slugify(f"{water_body}-{county}-{tpwaid}")

        # Create description
        description = f"Public {access_type.lower()} access at {water_body} in {county} County, Texas. TPWD public access point."

        # Extract data
        record = (
            name,
            slug,
            float(row.get('Latitude', 0)),
            float(row.get('Longitude', 0)),
            county,
            water_body,
            'boat_ramp',
            description,
            clean_amenities(row),
            'TPWD_Boat_Ramps',
            True,  # is_verified (official TPWD data)
            f"{water_body} Public Access - {county} County, Texas",  # meta_title
            f"Public fishing access at {water_body} in {county} County. Free {access_type.lower()} access point with GPS coordinates."  # meta_description
        )

        data_to_insert.append(record)

    # Define column names
    columns = [
        'name', 'slug', 'latitude', 'longitude', 'county', 'water_body_name',
        'spot_type', 'description', 'amenities', 'data_source', 'is_verified',
        'meta_title', 'meta_description'
    ]

    # Bulk insert
    try:
        rows_inserted = bulk_insert('fishing_spots', columns, data_to_insert)
        print(f"\n{'='*50}")
        print(f"SUCCESS: Imported {rows_inserted} boat ramps")
        print(f"{'='*50}")

        # Save processed data as JSON for reference
        processed_file = os.path.join(PROCESSED_DATA_DIR, 'boat_ramps_processed.json')
        df['slug'] = [record[1] for record in data_to_insert]
        df.to_json(processed_file, orient='records', indent=2)
        print(f"Processed data saved to: {processed_file}")

    except Exception as e:
        print(f"✗ Error during import: {e}")

if __name__ == "__main__":
    print("="*50)
    print("TPWD Boat Ramps ETL Script")
    print("="*50)

    process_boat_ramps()
