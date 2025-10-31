# Scaling Guide: Adding New States & Data Sources

This guide explains how to scale the fishing directory to support data from any state or source.

## Architecture Overview

The ETL pipeline uses the **Adapter Pattern** to handle different data formats:

```
Raw Data (CSV/JSON/API)
         ↓
   State Adapter (transforms to standard format)
         ↓
   Base ETL Framework (handles database insertion)
         ↓
    MySQL Database
```

## Quick Start: Adding a New State

### Option 1: Simple CSV with Standard Columns

If you have a CSV with columns like `name`, `latitude`, `longitude`, `county`, `water_body`:

```python
from adapters import GenericCSVAdapter

# Define column mapping
column_map = {
    'name': 'Site_Name',          # Your CSV column -> Our field
    'latitude': 'Lat',
    'longitude': 'Lon',
    'county': 'County_Name',
    'water_body': 'Waterbody',
    'spot_type': 'Access_Type',
    'description': 'Notes'
}

# Create adapter
adapter = GenericCSVAdapter(
    data_source_name="Colorado_Parks_Wildlife",
    state_code="CO",
    column_mapping=column_map
)

# Run import
adapter.process_and_import('raw-data/colorado_fishing.csv')
```

**That's it!** No custom Python code needed.

### Option 2: Custom State Adapter

For complex data formats, create a custom adapter:

1. **Copy template:**
   ```bash
   cp adapters/texas_tpwd_adapter.py adapters/your_state_adapter.py
   ```

2. **Implement required methods:**

```python
from etl_base import BaseDataAdapter, FishingSpotData
import pandas as pd

class YourStateAdapter(BaseDataAdapter):
    def __init__(self):
        super().__init__(
            data_source_name="Your_Data_Source",
            state_code="CO"  # Two-letter state code
        )

    def load_data(self, file_path: str) -> pd.DataFrame:
        """Load your data file (CSV, JSON, Excel, etc.)"""
        return pd.read_csv(file_path)

    def transform_row(self, row: pd.Series, index: int) -> FishingSpotData:
        """Map your data structure to our standard format"""

        return FishingSpotData(
            name=row['your_name_column'],
            latitude=float(row['your_lat_column']),
            longitude=float(row['your_lon_column']),
            county=row['your_county_column'],
            water_body_name=row['your_waterbody_column'],
            spot_type='boat_ramp',  # or pier, bank_fishing, state_park
            description=f"Public access at {row['your_waterbody_column']}",
            state='CO',
            amenities={
                'parking': row.get('parking') == 'Yes',
                'restrooms': row.get('restrooms') == 'Yes',
                # ... more amenities
            },
            source_id=row.get('unique_id'),
            is_verified=True
        )
```

3. **Run import:**
```python
adapter = YourStateAdapter()
adapter.process_and_import('raw-data/your_data.csv')
```

## StandardizedData Structure

All adapters must output `FishingSpotData` objects:

```python
@dataclass
class FishingSpotData:
    # Required fields
    name: str                   # "Lake Travis - Travis County Access"
    latitude: float             # 30.3922
    longitude: float            # -97.7431
    county: str                 # "Travis"
    water_body_name: str        # "Lake Travis"
    spot_type: str              # boat_ramp | pier | bank_fishing | state_park
    description: str            # "Public access at..."
    state: str                  # "TX" (2-letter code)

    # Optional fields
    amenities: Dict             # {'parking': True, 'restrooms': False}
    source_id: str              # Original ID from source system
    is_verified: bool           # True for official gov data
    meta_title: str             # SEO title
    meta_description: str       # SEO description
    address: str                # Full street address
    zip_code: str               # Zip/postal code
```

## Data Source Examples

### State Wildlife Agency Data

Most states publish fishing access data:

- **Texas:** TPWD Boat Ramps (CSV) - ✅ Implemented
- **California:** CDFW Fishing Access (JSON/CSV) - 📝 Template ready
- **Florida:** FWC Public Fishing Areas (CSV/API) - 📝 Template ready
- **Colorado:** CPW Fishing Atlas (Shapefile/CSV)
- **New York:** DEC Fishing Access (CSV)
- **Washington:** WDFW Access Sites (CSV)

### Other Data Sources

1. **State Parks with Fishing**
   - Download state park lists
   - Filter for fishing amenities
   - Use `spot_type='state_park'`

2. **Corps of Engineers**
   - USACE recreation.gov data
   - Lake/reservoir access points

3. **User Submissions**
   - Community-contributed spots
   - Set `is_verified=False`
   - Require admin approval

4. **Web Scraping**
   - Use BeautifulSoup/Scrapy
   - Parse HTML tables
   - Feed into Generic CSV adapter

## Column Mapping Reference

Common column name variations:

| Our Field | Common Variations |
|-----------|------------------|
| name | Site_Name, Location_Name, Access_Point, Ramp_Name |
| latitude | Lat, Latitude, LAT, Y, Northing |
| longitude | Lon, Longitude, LON, LONG, X, Easting |
| county | County_Name, COUNTY, Admin_Unit |
| water_body | Waterbody, Water_Body, Lake_Name, River_Name |
| spot_type | Access_Type, Facility_Type, Type |

## Database Migration

Before importing non-Texas data, run the migration:

```bash
cd data-pipeline
mysql -u fishing_user -p fishing_directory < migrations/001_add_state_fields.sql
```

This adds:
- `state` (VARCHAR(2)) - Two-letter state code
- `address` (VARCHAR(255)) - Full street address
- `zip_code` (VARCHAR(10)) - Zip/postal code

## Running Multiple States

Create a master import script:

```python
# import_all_states.py
from adapters import (
    TexasTPWDAdapter,
    CaliforniaDFWAdapter,
    FloridaFWCAdapter,
    GenericCSVAdapter
)

def import_all():
    # Texas
    print("\n=== Importing Texas ===\")
    tx = TexasTPWDAdapter()
    tx.process_and_import('raw-data/tpwd_boat_ramps.csv')

    # California
    print("\n=== Importing California ===\")
    ca = CaliforniaDFWAdapter()
    ca.process_and_import('raw-data/california_fishing_access.json')

    # Colorado (using generic adapter)
    print("\n=== Importing Colorado ===\")
    co_map = {
        'name': 'Site Name',
        'latitude': 'Latitude',
        'longitude': 'Longitude',
        'county': 'County',
        'water_body': 'Waterbody Name'
    }
    co = GenericCSVAdapter("CPW_Fishing", "CO", co_map)
    co.process_and_import('raw-data/colorado_fishing.csv')

    print("\n✅ All states imported successfully!")

if __name__ == "__main__":
    import_all()
```

## Performance Tips

### For Large Datasets (10,000+ records)

1. **Bulk Insert**
   - Already implemented in `db_utils.bulk_insert()`
   - Inserts 1000 rows at a time

2. **Disable Duplicate Slug Checking**
   - If you pre-generate unique slugs
   - Bypass `check_duplicate_slug()` calls

3. **Database Indexing**
   - Already indexed: `state`, `county`, `spot_type`
   - For geo searches, add spatial index:
   ```sql
   ALTER TABLE fishing_spots
   ADD SPATIAL INDEX idx_location (location);
   ```

4. **Parallel Processing**
   ```python
   from multiprocessing import Pool

   def process_state(adapter_class):
       adapter = adapter_class()
       return adapter.process_and_import(...)

   with Pool(4) as pool:
       pool.map(process_state, [TexasAdapter, CaliforniaAdapter, ...])
   ```

## Testing New Adapters

1. **Test with sample data:**
   ```python
   # Create test CSV with 10-20 rows
   adapter = YourAdapter()
   adapter.process_and_import('test_sample.csv')
   ```

2. **Check database:**
   ```sql
   SELECT * FROM fishing_spots WHERE state = 'CO' LIMIT 10;
   ```

3. **Verify on frontend:**
   - Visit http://localhost:4321/colorado
   - Search for spots
   - Check map display

4. **Run full import:**
   ```python
   adapter.process_and_import('full_dataset.csv')
   ```

## Troubleshooting

### Common Issues

**"Column not found"**
- Check CSV column names exactly (case-sensitive)
- Print first row: `df.iloc[0]` to see column names

**"Invalid coordinates"**
- Some rows may have 0, NULL, or invalid lat/long
- Adapter skips these automatically
- Check original data quality

**"Duplicate slug"**
- Two spots with same name in same county
- Provide unique `source_id` in your data
- Or adapter will auto-increment: `slug-1`, `slug-2`

**"Encoding errors"**
- Use `encoding='utf-8'` or `encoding='latin-1'`
- Handle special characters: `name.encode('ascii', 'ignore')`

## Next Steps

1. **Add more states**
   - Find data sources
   - Create adapters
   - Run imports

2. **Add state pages**
   - Create `/california`, `/florida`, etc. pages
   - Copy [frontend/src/pages/texas.astro](../frontend/src/pages/texas.astro)
   - Update queries: `WHERE state = 'CA'`

3. **Update homepage**
   - Add state selector
   - Show counts per state
   - National search

4. **Add mapping**
   - Integrate Google Maps / Mapbox
   - Cluster markers by state
   - Geo-search by radius

## Questions?

The ETL framework is designed to be flexible and extensible. If you run into issues:

1. Check the example adapters in `adapters/`
2. Review this guide
3. Test with small sample data first
4. Open an issue if you need help

Happy scaling! 🎣
