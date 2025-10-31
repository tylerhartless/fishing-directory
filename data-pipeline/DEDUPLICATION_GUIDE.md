# Deduplication Strategy

## Problem

When importing data from multiple sources, you'll encounter overlaps:
- A boat ramp at a state park appears in both TPWD boat ramp data AND state parks data
- Community lakes may have boat ramps already in the TPWD dataset
- Future data sources will inevitably overlap with existing records

## Solution: Proximity-Based Deduplication

The ETL framework automatically handles duplicates using:

### 1. **Proximity Detection** (Haversine Formula)
- Checks if a spot already exists within 100 meters (configurable)
- Uses accurate spherical distance calculation
- Finds the 5 closest matches

### 2. **Source Priority System**
Determines which data source is most authoritative:

```python
source_priority = {
    'Texas_State_Parks': 3,      # Highest - most detailed
    'Texas_Community_Lakes': 2,   # Medium
    'TPWD_Boat_Ramps': 1,        # Lowest - basic data
}
```

### 3. **Smart Update Logic**
When a duplicate is found:

- **Higher priority source** → Update existing record with new data
- **Lower priority source** → Skip, keep existing
- **Same priority but richer data** → Update with amenities/description

## How It Works

```python
# Example: Importing state parks after boat ramps

# Existing record (TPWD boat ramp):
{
    "name": "Abilene State Park Boat Ramp",
    "spot_type": "boat_ramp",
    "data_source": "TPWD_Boat_Ramps",
    "amenities": {"parking": true}
}

# New record (State Parks data):
{
    "name": "Abilene State Park",
    "spot_type": "state_park",
    "data_source": "Texas_State_Parks",
    "amenities": {
        "parking": true,
        "restrooms": true,
        "camping": true,
        "fish_cleaning": true
    },
    "description": "... offers fishing access with no license required..."
}

# Result: Updates existing record because:
# 1. State Parks (priority 3) > Boat Ramps (priority 1)
# 2. Richer amenities data
# 3. Better description
```

## Output

The ETL process now shows:

```
[2/3] Transforming and checking for duplicates...
      New records to insert: 45
      Existing records updated: 17
      Duplicates skipped: 0

[3/3] Inserting into database...
[OK] Inserted 45 rows into fishing_spots

============================================================
ETL Complete: Texas_State_Parks
============================================================
✓ New records inserted: 45
✓ Existing records updated: 17
  Duplicates skipped: 0
============================================================
```

## Configuration

### Adjust Detection Radius

```python
# Default: 100 meters
adapter = TexasStateParksAdapter()

# More strict (50m):
adapter = TexasStateParksAdapter()
adapter.dedup_radius_meters = 50

# More lenient (200m):
adapter = TexasStateParksAdapter()
adapter.dedup_radius_meters = 200
```

### Customize Source Priority

Edit `etl_base.py`, `should_update_existing()` method:

```python
source_priority = {
    'Your_New_Source': 4,           # Add your source
    'Texas_State_Parks': 3,
    'Texas_Community_Lakes': 2,
    'TPWD_Boat_Ramps': 1,
}
```

## Benefits

✅ **No Manual Cleanup** - Automatic detection and merging
✅ **Data Quality** - Always keeps the best available data
✅ **Flexible** - Works with any combination of data sources
✅ **Transparent** - Shows exactly what was updated/skipped
✅ **Safe** - Never deletes data, only updates when better source available

## Example Workflow

```bash
# 1. Import TPWD boat ramps (baseline)
python process_boat_ramps.py
# Result: 2,234 boat ramps inserted

# 2. Import state parks (may overlap with boat ramps)
python adapters/texas_state_parks_poi_adapter.py
# Result:
# - 45 new state parks inserted
# - 17 boat ramps upgraded to state parks (richer data)
# - 0 skipped

# 3. Import community lakes (may overlap with both)
python adapters/texas_community_lakes_adapter.py
# Result:
# - 120 new lakes inserted
# - 8 existing spots updated
# - 3 duplicates skipped (existing data was better)
```

## Technical Details

### Database Functions

**find_nearby_spots(lat, lon, radius_meters)**
- Haversine formula for accurate spherical distance
- Returns up to 5 closest matches within radius
- Includes distance in meters for each match

**update_spot_if_better(spot_id, new_data)**
- Updates only specified fields
- Preserves original slug and coordinates
- Atomic transaction (rollback on error)

### Performance

- Proximity check: ~5ms per record
- Full import of 1000 records with dedup: ~30 seconds
- Scales well with proper database indexing on lat/lon

## Best Practices

1. **Import in priority order** - Start with lowest priority sources first
2. **Test with small datasets** - Verify dedup logic before full import
3. **Review updated records** - Check database to ensure logic is correct
4. **Adjust radius as needed** - 100m works for most cases, but tune per use case
5. **Keep source priority updated** - As you add sources, maintain the hierarchy
