"""
ETL Script: Process Texas State Parks with Fishing Access

State parks offer FREE fishing without a license!

Data Source: Manual entry or Texas Parks & Wildlife website
You can also scrape: https://tpwd.texas.gov/state-parks/parks/find-a-park
"""

from db_utils import bulk_insert
from slugify import slugify
import json

# Sample state parks with fishing (expand this list!)
STATE_PARKS_DATA = [
    {
        'name': 'Brazos Bend State Park',
        'county': 'Fort Bend',
        'latitude': 29.3611,
        'longitude': -95.5964,
        'water_body': 'Park Lakes',
        'description': 'Excellent fishing for bass, catfish, and sunfish. No fishing license required at state parks! Multiple fishing piers and bank access.',
        'amenities': {
            'parking': True,
            'restrooms': True,
            'lighting': False,
            'fish_cleaning': True,
            'camping': True,
            'fishing_pier': True
        }
    },
    {
        'name': 'Inks Lake State Park',
        'county': 'Burnet',
        'latitude': 30.7325,
        'longitude': -98.3678,
        'water_body': 'Inks Lake',
        'description': 'Year-round fishing for largemouth bass, striped bass, catfish, and white bass. Boat ramp and fishing pier available.',
        'amenities': {
            'parking': True,
            'restrooms': True,
            'lighting': True,
            'boat_trailer_parking': True,
            'camping': True,
            'fishing_pier': True
        }
    },
    {
        'name': 'Lake Brownwood State Park',
        'county': 'Brown',
        'latitude': 31.8453,
        'longitude': -99.0089,
        'water_body': 'Lake Brownwood',
        'description': 'Popular for crappie, catfish, and bass fishing. Fishing pier and boat ramp on site.',
        'amenities': {
            'parking': True,
            'restrooms': True,
            'lighting': False,
            'boat_trailer_parking': True,
            'camping': True,
            'fishing_pier': True
        }
    },
    # Add more state parks here...
]

def process_state_parks():
    """Process state parks data and insert into database"""

    print(f"Processing {len(STATE_PARKS_DATA)} state parks...")

    data_to_insert = []

    for park in STATE_PARKS_DATA:
        slug = slugify(f"{park['name']}-{park['county']}")

        record = (
            park['name'],
            slug,
            park['latitude'],
            park['longitude'],
            park['county'],
            park['water_body'],
            'state_park',
            park['description'] + '\n\n⭐ FREE FISHING - No license required at Texas State Parks!',
            json.dumps(park['amenities']),
            'Texas_State_Parks',
            True,  # is_verified
            f"{park['name']} Fishing - Free License-Free Fishing in {park['county']} County",
            f"Free fishing at {park['name']}! No license required. {park['water_body']} offers great opportunities for anglers."
        )

        data_to_insert.append(record)

    columns = [
        'name', 'slug', 'latitude', 'longitude', 'county', 'water_body_name',
        'spot_type', 'description', 'amenities', 'data_source', 'is_verified',
        'meta_title', 'meta_description'
    ]

    rows_inserted = bulk_insert('fishing_spots', columns, data_to_insert)

    print(f"\n{'='*50}")
    print(f"SUCCESS: Imported {rows_inserted} state parks")
    print(f"{'='*50}")

if __name__ == "__main__":
    print("="*50)
    print("Texas State Parks ETL Script")
    print("="*50)

    process_state_parks()
