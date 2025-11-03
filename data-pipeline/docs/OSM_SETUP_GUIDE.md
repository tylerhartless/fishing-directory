# OpenStreetMap Local Database Setup Guide

## Overview

We're using the **US South** regional extract from Geofabrik which covers:
- Texas (current focus)
- Louisiana, Arkansas, Oklahoma
- Mississippi, Alabama, Tennessee
- Florida, Georgia, South Carolina, North Carolina

**File size:** ~3.6 GB (compressed PBF)
**Coverage:** Perfect for southeastern US expansion

## Download

```bash
cd data-pipeline/osm/

# Download US South extract from Geofabrik
wget https://download.geofabrik.de/north-america/us-south-latest.osm.pbf

# Verify download
ls -lh us-south-latest.osm.pbf
# Should show ~3.6 GB
```

## Setup Options

### Option 1: PostGIS (Recommended for Rich Queries)

**Pros:**
- Full SQL queries with spatial functions
- Can join multiple OSM tables
- Standard PostgreSQL tooling
- Good for complex analysis

**Cons:**
- Requires PostgreSQL + PostGIS
- Initial import takes ~30-45 minutes
- Uses ~15-20 GB disk space after import

**Setup:**
```bash
# Install PostgreSQL and PostGIS (if not already installed)
# Ubuntu/Debian:
sudo apt install postgresql postgis

# macOS:
brew install postgresql postgis

# Windows: Download from postgresql.org

# Create database
createdb fishing_osm

# Enable PostGIS extension
psql fishing_osm -c "CREATE EXTENSION postgis;"
psql fishing_osm -c "CREATE EXTENSION hstore;"

# Import OSM data
osm2pgsql -c -d fishing_osm \
  --create \
  --slim \
  -G \
  --hstore \
  --multi-geometry \
  --number-processes 4 \
  --cache 4096 \
  us-south-latest.osm.pbf

# This takes 30-45 minutes for 3.6 GB file
# Watch progress in terminal
```

**Verify Import:**
```sql
-- Check tables created
\dt

-- Should see:
-- planet_osm_point
-- planet_osm_line
-- planet_osm_polygon
-- planet_osm_roads

-- Count water bodies
SELECT COUNT(*) FROM planet_osm_polygon
WHERE natural = 'water' OR water IN ('lake', 'pond', 'reservoir');

-- Should be thousands across the region
```

### Option 2: Osmium (Lighter Weight)

**Pros:**
- No database required
- Faster setup (~5 minutes)
- Less disk space (~4-5 GB)
- Good for simple proximity queries

**Cons:**
- More manual coding required
- No SQL query interface
- Need to rebuild spatial index for searches

**Setup:**
```bash
# Install osmium
pip install osmium

# No database import needed!
# Query directly from PBF file
```

**Usage Example:**
```python
import osmium

class WaterBodyFinder(osmium.SimpleHandler):
    def __init__(self, target_lat, target_lon, radius_km=0.5):
        super().__init__()
        self.target = (target_lat, target_lon)
        self.radius = radius_km
        self.results = []

    def way(self, w):
        # Check if it's a water body
        if (w.tags.get('natural') == 'water' or
            w.tags.get('water') in ['lake', 'pond', 'reservoir']):

            # Simple proximity check
            # (In practice, you'd use proper distance calculation)
            if self._is_nearby(w):
                self.results.append({
                    'name': w.tags.get('name'),
                    'type': w.tags.get('water', 'water')
                })

handler = WaterBodyFinder(29.7604, -95.3698)
handler.apply_file('us-south-latest.osm.pbf')
print(handler.results)
```

## Recommended: PostGIS Approach

For this project, **PostGIS is recommended** because:
1. Rich spatial queries for water bodies, parks, amenities
2. Can analyze OSM data quality across states
3. One-time setup, then fast queries
4. Standard SQL makes debugging easier

## PostGIS Database Schema

After import, you'll have these tables:

### planet_osm_polygon
Contains areas like lakes, ponds, parks:
```sql
-- Key columns:
name          -- Name of feature
natural       -- 'water' for water bodies
water         -- 'lake', 'pond', 'reservoir'
leisure       -- 'park', 'nature_reserve'
way           -- PostGIS geometry
way_area      -- Area in sq meters
```

### planet_osm_point
Contains point features like amenities:
```sql
-- Key columns:
name          -- Name of feature
amenity       -- 'parking', 'toilets', 'picnic_site'
leisure       -- 'slipway', 'fishing', 'marina'
way           -- PostGIS geometry (point)
```

### planet_osm_line
Contains linear features like rivers:
```sql
-- Key columns:
name          -- Name of feature
waterway      -- 'river', 'stream', 'canal'
natural       -- Various natural features
way           -- PostGIS geometry (linestring)
```

## Example Queries

### Find Water Bodies Near Coordinates
```sql
SELECT
    name,
    CASE
        WHEN water IS NOT NULL THEN water
        WHEN natural = 'water' THEN 'water'
    END as water_type,
    way_area / 1000000.0 as area_km2,
    ST_Distance(
        ST_Transform(way, 4326)::geography,
        ST_SetSRID(ST_MakePoint(-95.3698, 29.7604), 4326)::geography
    ) as distance_meters
FROM planet_osm_polygon
WHERE (natural = 'water' OR water IN ('lake', 'pond', 'reservoir'))
  AND name IS NOT NULL
  AND ST_DWithin(
    ST_Transform(way, 4326)::geography,
    ST_SetSRID(ST_MakePoint(-95.3698, 29.7604), 4326)::geography,
    500  -- 500 meter radius
  )
ORDER BY distance_meters
LIMIT 5;
```

### Find Parks Near Coordinates
```sql
SELECT
    name,
    leisure,
    ST_Distance(
        ST_Transform(way, 4326)::geography,
        ST_SetSRID(ST_MakePoint(-95.3698, 29.7604), 4326)::geography
    ) as distance_meters
FROM planet_osm_polygon
WHERE leisure IN ('park', 'nature_reserve')
  AND name IS NOT NULL
  AND ST_DWithin(
    ST_Transform(way, 4326)::geography,
    ST_SetSRID(ST_MakePoint(-95.3698, 29.7604), 4326)::geography,
    300  -- 300 meter radius
  )
ORDER BY distance_meters
LIMIT 3;
```

### Find Amenities Near Coordinates
```sql
SELECT
    amenity,
    leisure,
    COUNT(*) as count
FROM planet_osm_point
WHERE (
    amenity IN ('parking', 'toilets', 'picnic_site')
    OR leisure IN ('slipway', 'fishing', 'marina', 'picnic_table')
  )
  AND ST_DWithin(
    ST_Transform(way, 4326)::geography,
    ST_SetSRID(ST_MakePoint(-95.3698, 29.7604), 4326)::geography,
    500  -- 500 meter radius
  )
GROUP BY amenity, leisure;
```

### Check Coverage by State
```sql
-- Count water bodies per state (using boundary polygons)
SELECT
    tags->'name' as state_name,
    COUNT(*) as water_body_count
FROM planet_osm_polygon water
JOIN planet_osm_polygon boundaries ON
    ST_Contains(boundaries.way, ST_Centroid(water.way))
WHERE water.natural = 'water'
  AND water.name IS NOT NULL
  AND boundaries.boundary = 'administrative'
  AND boundaries.admin_level = '4'  -- State level
GROUP BY tags->'name'
ORDER BY water_body_count DESC;
```

## State Coverage Analysis

Once imported, analyze which states have best OSM coverage:

```sql
-- Water bodies with names by state
SELECT
    b.tags->'name' as state,
    COUNT(*) FILTER (WHERE w.water = 'lake') as lakes,
    COUNT(*) FILTER (WHERE w.water = 'pond') as ponds,
    COUNT(*) FILTER (WHERE w.water = 'reservoir') as reservoirs,
    COUNT(*) as total_water_bodies
FROM planet_osm_polygon w
JOIN planet_osm_polygon b ON
    ST_Contains(b.way, ST_Centroid(w.way))
WHERE w.natural = 'water'
  AND w.name IS NOT NULL
  AND b.boundary = 'administrative'
  AND b.admin_level = '4'
GROUP BY b.tags->'name'
ORDER BY total_water_bodies DESC;
```

This will help you decide which state to tackle next based on OSM data quality!

## Performance Tips

### Create Spatial Indexes
```sql
-- These should already exist from osm2pgsql, but verify:
\di planet_osm_*

-- If missing, create:
CREATE INDEX IF NOT EXISTS idx_polygon_way
  ON planet_osm_polygon USING GIST (way);

CREATE INDEX IF NOT EXISTS idx_point_way
  ON planet_osm_point USING GIST (way);

CREATE INDEX IF NOT EXISTS idx_polygon_water
  ON planet_osm_polygon (natural, water)
  WHERE natural = 'water' OR water IS NOT NULL;
```

### Optimize Queries
```sql
-- Use geography casts for distance calculations
-- Good:
ST_DWithin(
  ST_Transform(way, 4326)::geography,
  ST_SetSRID(ST_MakePoint(lon, lat), 4326)::geography,
  radius
)

-- Avoid:
ST_Distance(way, point) < radius  -- Doesn't use index well
```

### Connection Pooling
For production enrichment, use connection pooling:
```python
from psycopg2.pool import SimpleConnectionPool

pool = SimpleConnectionPool(
    minconn=1,
    maxconn=10,
    dbname='fishing_osm',
    user='postgres'
)
```

## Next Steps After Import

1. **Verify coverage** - Run state analysis query
2. **Test queries** - Try finding water bodies in different states
3. **Update enrichment script** - Point to local DB instead of Overpass API
4. **Benchmark** - Compare speed vs Overpass (should be 100x faster)
5. **Choose next state** - Based on OSM coverage quality

## Troubleshooting

### Import Fails with Memory Error
```bash
# Reduce cache size
osm2pgsql --cache 2048 us-south-latest.osm.pbf
```

### Slow Queries
```sql
-- Analyze tables to update statistics
ANALYZE planet_osm_polygon;
ANALYZE planet_osm_point;
ANALYZE planet_osm_line;

-- Vacuum if needed
VACUUM ANALYZE;
```

### Missing Data
```sql
-- Check what data exists in your area
SELECT DISTINCT tags FROM planet_osm_polygon
WHERE ST_Contains(
  ST_MakeEnvelope(-106.65, 25.84, -93.51, 36.50, 4326),  -- Texas bounds
  ST_Transform(way, 4326)
)
LIMIT 100;
```

## Storage Requirements

- **PBF file:** 3.6 GB
- **PostGIS import:** ~15-20 GB
- **Total:** ~20-25 GB free space needed

## Update Frequency

OSM data changes frequently. Plan to re-download and re-import:
- **Monthly:** For active development
- **Quarterly:** For production use

```bash
# Update script
cd data-pipeline/osm/
wget -N https://download.geofabrik.de/north-america/us-south-latest.osm.pbf
# -N flag only downloads if newer version exists
```
