# Data Pipeline Architecture v2.0

## Overview

This document outlines the redesigned data pipeline for the Texas Fishing Directory, with a focus on staging, validation, and enrichment before database commits.

## Current Problems

1. **Inconsistent data quality** - City PDFs had better facility names than community lake scrapes
2. **No staging process** - Data goes directly to DB without validation
3. **Difficult to reproduce** - Hard to re-import all Texas data cleanly
4. **Manual fixes required** - Many post-import corrections needed
5. **OSM API rate limiting** - Overpass API queries are slow and unreliable for bulk operations
6. **No clear source priority** - Don't know which data source to trust when there's a conflict

## Proposed Architecture

### Phase 1: Data Ingestion (Extract)
```
Raw Sources → Adapters → Staged JSON
```

**Sources:**
- TPWD Boat Ramps (authoritative for boat ramps)
- TPWD Community Fishing Lakes (authoritative for stocking info)
- TPWD Neighborhood Fishing Program (authoritative for stocking info)
- TPWD State Parks (authoritative for state park info)
- City PDFs (authoritative for local facility names)
- Texas Lakes scrape (good for large lakes)
- RACA data (good for reservoir access points)

**Output:** `staged/raw/{source_name}_{timestamp}.json`

Each adapter produces standardized JSON:
```json
{
  "source": "Texas_City_PDFs_Houston",
  "extracted_at": "2025-01-15T10:30:00Z",
  "entries": [
    {
      "name": "Park Name",
      "water_body": "Lake Name",
      "latitude": 29.7604,
      "longitude": -95.3698,
      "address": "123 Main St",
      "county": "Harris",
      "spot_type": "public_water",
      "amenities": {...},
      "description": "...",
      "source_url": "...",
      "confidence": 0.9
    }
  ]
}
```

### Phase 2: Enrichment & Validation (Transform)
```
Staged JSON → Enrichment → Validation → Validated JSON
```

**2.1 Local OSM Enrichment**
- Download Texas OSM extract from Geofabrik (~500MB)
- Use local PostGIS or Osmium tools for offline queries
- Much faster than Overpass API
- No rate limiting
- Enrichment adds:
  - Missing addresses
  - Additional amenities
  - Better water body names
  - Facility names

**2.2 Deduplication**
- Check for exact name + county matches
- Check for nearby coordinates (100m radius)
- Flag potential duplicates for manual review
- Create `duplicates_review.json` with suggestions

**2.3 Source Priority Resolution**
When multiple sources have the same spot:
1. **Coordinates**: Use source with highest confidence (usually GPS-based)
2. **Facility Name**: City PDFs > Community Lakes > State Parks > Lakes scrape
3. **Water Body Name**: OSM > Community Lakes > Lakes scrape
4. **Amenities**: Merge all sources (union of amenities)
5. **Address**: City PDFs > OSM > others
6. **Stocking Info**: TPWD sources are authoritative

**Output:** `staged/validated/{batch_name}_{timestamp}.json`

### Phase 3: Database Commit (Load)
```
Validated JSON → Database
```

- Atomic batch commits
- Rollback on validation failure
- Generate commit report showing:
  - New spots added
  - Existing spots updated
  - Duplicates skipped
  - Errors encountered

**Output:** `staged/reports/{batch_name}_commit_{timestamp}.json`

## Implementation Plan

### Step 1: Download Texas OSM Data
```bash
# Download Texas extract from Geofabrik
wget https://download.geofabrik.de/north-america/us/texas-latest.osm.pbf

# Convert to PostgreSQL database with PostGIS
osm2pgsql -c -d fishing_osm -U postgres texas-latest.osm.pbf
```

### Step 2: Create Staging Directory Structure
```
data-pipeline/
  staged/
    raw/           # Raw extracts from each source
    enriched/      # After OSM enrichment
    validated/     # After deduplication & validation
    reports/       # Import reports
    duplicates/    # Duplicate review files
```

### Step 3: Refactor Adapters
Each adapter should:
1. Extract data from source
2. Output standardized JSON to `staged/raw/`
3. Include confidence scores
4. Include source metadata

### Step 4: Build Enrichment Pipeline
```python
# enrich_pipeline.py
1. Load raw JSON
2. Query local OSM database for each coordinate
3. Apply source priority rules
4. Detect duplicates
5. Output to staged/validated/
```

### Step 5: Build Commit Pipeline
```python
# commit_pipeline.py
1. Load validated JSON
2. Start database transaction
3. Insert/update spots
4. Generate report
5. Commit or rollback
```

### Step 6: Test with Texas Data
```bash
# Clear database
python scripts/clear_database.py

# Run full pipeline
python pipeline/run_full_import.py --state TX --validate-only

# Review validation report
cat staged/reports/texas_validation_report.json

# If good, commit
python pipeline/run_full_import.py --state TX --commit
```

## Source Priority Matrix

| Data Field | Priority Order |
|------------|---------------|
| Coordinates | GPS > Geocoded > Manual |
| Facility Name | City PDF > Community Lake > State Park > Lake Scrape |
| Water Body | OSM > Community Lake > Lake Scrape |
| Address | City PDF > OSM > Geocoded |
| Amenities | Merge all (union) |
| Stocking | TPWD only (authoritative) |
| County | Reverse geocode (authoritative) |
| Description | Generated from spot_type + stocking info |

## Local OSM Query Examples

### Using PostGIS:
```sql
-- Find water bodies near coordinates
SELECT name, ST_Distance(
  ST_Transform(way, 4326)::geography,
  ST_SetSRID(ST_MakePoint(-95.3698, 29.7604), 4326)::geography
) as distance_meters
FROM planet_osm_polygon
WHERE natural = 'water' OR water IN ('lake', 'pond', 'reservoir')
  AND ST_DWithin(
    ST_Transform(way, 4326)::geography,
    ST_SetSRID(ST_MakePoint(-95.3698, 29.7604), 4326)::geography,
    500
  )
ORDER BY distance_meters
LIMIT 5;
```

### Using Osmium (alternative):
```python
import osmium

class WaterBodyFinder(osmium.SimpleHandler):
    def __init__(self, lat, lon, radius=500):
        super().__init__()
        self.target = (lat, lon)
        self.radius = radius
        self.results = []

    def way(self, w):
        if w.tags.get('natural') == 'water' or w.tags.get('water') in ['lake', 'pond']:
            # Calculate distance and collect results
            pass
```

## Benefits of New Architecture

1. ✅ **Reproducible** - Can re-import all Texas data cleanly
2. ✅ **Auditable** - JSON files show exactly what was imported
3. ✅ **Testable** - Validate before committing
4. ✅ **Scalable** - Works for other states
5. ✅ **Fast** - Local OSM queries are 100x faster than Overpass
6. ✅ **Reliable** - No API rate limits
7. ✅ **Quality** - Source priority ensures best data wins
8. ✅ **Safe** - Staging prevents bad data from reaching DB

## Migration Path

1. **Finish current OSM enrichment** for existing data
2. **Download Texas OSM extract** and set up local database
3. **Create staging directory structure**
4. **Refactor one adapter** (start with Community Lakes)
5. **Test with small dataset** (one county)
6. **Expand to all adapters**
7. **Run full Texas reimport** and compare with current data
8. **Document differences** and resolve
9. **Commit when satisfied**
10. **Use as template** for other states

## Next Steps

1. Let current OSM enrichment complete
2. Review results and finalize Texas data
3. Set up local OSM database for Texas
4. Create staging infrastructure
5. Refactor adapters one by one
6. Test full reimport pipeline
7. Document for future states
