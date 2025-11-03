# PostGIS Import Plan for Address Enrichment

## Why Import Local OSM Data Now

### Problem
- 742 public_water spots (91.2%) have no addresses
- Reverse geocoding gives generic roads, not facility names
- Need to match water bodies to their parent facilities (parks, reserves, etc.)

### Solution
Import OSM data to PostGIS and query for nearest facilities with addresses

## What We'll Get

### From OSM Data
```sql
-- Find nearest park/facility to a water body
SELECT
    name,
    tags->'addr:full' as address,
    tags->'addr:street' as street,
    tags->'addr:city' as city,
    ST_Distance(way, point) as distance_meters
FROM planet_osm_polygon
WHERE
    (leisure IN ('park', 'nature_reserve') OR
     boundary = 'protected_area' OR
     amenity = 'community_centre')
    AND ST_DWithin(way, point, 1000)  -- Within 1km
ORDER BY distance_meters
LIMIT 1;
```

###Example Matches
```
Blue Lake → Palestine City Park (123 Park St, Palestine, TX)
Ellen Trout Zoo Lake → Ellen Trout Park (402 Zoo Circle, Lufkin, TX)
Lost Maples Pond → Lost Maples State Natural Area (37221 RR 187, Vanderpool, TX)
```

## Implementation Steps

### Phase 1: Docker PostGIS Setup (10 minutes)

```bash
# 1. Create PostGIS container
docker run -d --name osm-postgis \
  -e POSTGRES_PASSWORD=fishing_directory \
  -e POSTGRES_USER=osm \
  -e POSTGRES_DB=gis \
  -p 5433:5432 \
  -v osm-data:/var/lib/postgresql/data \
  postgis/postgis:16-3.4

# 2. Verify it's running
docker ps | grep osm-postgis
```

### Phase 2: Install osm2pgsql (10 minutes)

**Windows:**
```bash
# Download from: https://github.com/osm2pgsql-dev/osm2pgsql/releases
# Or use chocolatey:
choco install osm2pgsql
```

**Verify:**
```bash
osm2pgsql --version
```

### Phase 3: Import OSM Data (2-4 hours)

```bash
cd c:\Users\tyash\Desktop\fishing-directory\data-pipeline\osm

# Import with optimized settings
osm2pgsql \
  -d gis \
  -U osm \
  -H localhost \
  -P 5433 \
  --create \
  --slim \
  -G \
  --hstore \
  --tag-transform-script <path-to-osm2pgsql>\default.style \
  --number-processes 4 \
  us-south-251101.osm.pbf
```

**Progress indicators:**
- Processing nodes: ~30 minutes
- Processing ways: ~1 hour
- Processing relations: ~30 minutes
- Creating indexes: ~1-2 hours

### Phase 4: Create Spatial Indexes (30 minutes)

```sql
-- Connect to database
psql -U osm -h localhost -p 5433 -d gis

-- Indexes will be created automatically by osm2pgsql
-- Verify:
\di planet_osm_*

-- Should see indexes on:
-- - planet_osm_point
-- - planet_osm_line
-- - planet_osm_polygon
-- - planet_osm_roads
```

### Phase 5: Test Queries (10 minutes)

```sql
-- Test: Find parks near a fishing spot
SELECT
    osm_id,
    name,
    leisure,
    tags->'addr:street' as street,
    tags->'addr:city' as city,
    ST_Distance(
        way::geography,
        ST_SetSRID(ST_MakePoint(-95.6552, 31.7630), 4326)::geography
    ) as distance_meters
FROM planet_osm_polygon
WHERE
    leisure = 'park'
    AND ST_DWithin(
        way::geography,
        ST_SetSRID(ST_MakePoint(-95.6552, 31.7630), 4326)::geography,
        1000
    )
ORDER BY distance_meters
LIMIT 5;
```

### Phase 6: Python Integration (30 minutes)

```python
# Install psycopg2
pip install psycopg2-binary

# Create enrichment script
import psycopg2

conn = psycopg2.connect(
    host='localhost',
    port=5433,
    database='gis',
    user='osm',
    password='fishing_directory'
)

def find_nearest_facility(lat, lon, radius_meters=1000):
    """Find nearest park/facility with address"""
    query = """
        SELECT
            name,
            leisure,
            tourism,
            tags->'addr:street' as street,
            tags->'addr:housenumber' as house_number,
            tags->'addr:city' as city,
            tags->'addr:postcode' as postcode,
            ST_Distance(
                way::geography,
                ST_SetSRID(ST_MakePoint(%s, %s), 4326)::geography
            ) as distance_meters
        FROM planet_osm_polygon
        WHERE
            (leisure IN ('park', 'nature_reserve', 'recreation_ground')
             OR tourism IN ('attraction', 'information')
             OR boundary = 'protected_area')
            AND ST_DWithin(
                way::geography,
                ST_SetSRID(ST_MakePoint(%s, %s), 4326)::geography,
                %s
            )
        ORDER BY distance_meters
        LIMIT 1;
    """

    cur = conn.cursor()
    cur.execute(query, (lon, lat, lon, lat, radius_meters))
    result = cur.fetchone()

    if result:
        return {
            'facility_name': result[0],
            'facility_type': result[1] or result[2],
            'street': result[3],
            'house_number': result[4],
            'city': result[5],
            'postcode': result[6],
            'distance_meters': result[7]
        }
    return None
```

## Expected Results

### Address Coverage After Import
```
Current:
  State Parks:    62/62   (100.0%) ✅
  Public Water:   72/814  (  8.8%) ❌
  River Access:   10/29   ( 34.5%) ❌

After OSM Enrichment:
  State Parks:    62/62   (100.0%) ✅ (no change)
  Public Water:  400/814  ( 49.1%) ⬆️ +328 addresses
  River Access:   20/29   ( 69.0%) ⬆️ +10 addresses
```

**Why not 100%?**
- Some spots are truly remote (Wildlife Management Areas)
- Some are unnamed water bodies without nearby facilities
- Some are in areas with limited OSM data

But 49% is much better than 9%!

## Time Investment

| Phase | Time | Effort |
|-------|------|--------|
| Docker setup | 10 min | Low |
| Install osm2pgsql | 10 min | Low |
| **Import OSM (waiting)** | **2-4 hours** | **None (automated)** |
| Create indexes (auto) | 30 min | None |
| Test queries | 10 min | Medium |
| Python integration | 30 min | Medium |
| Run enrichment | 10 min | Low |
| **TOTAL ACTIVE WORK** | **70 min** | |
| **TOTAL WAIT TIME** | **2.5-4.5 hours** | |

## Decision

### ✅ RECOMMEND POSTGIS IMPORT

**Reasons:**
1. **Immediate value**: Get 300+ new addresses
2. **Better addresses**: Real facility names, not generic roads
3. **Future-proof**: Ready for LA, FL, GA, AL expansion
4. **One-time cost**: 4 hours import, unlimited future queries
5. **Professional setup**: Spatial database = industry standard

### Timeline
1. **Today**: Start import before end of session (set it and forget it)
2. **Tomorrow**: Verify import, create enrichment script
3. **Day 3**: Run address enrichment, apply results

## Alternative: Skip PostGIS

If you don't want to spend 4 hours importing:
1. Apply current Overpass API enrichment (amenities only)
2. Use Nominatim reverse geocoding for generic addresses
3. Manually improve addresses over time

But PostGIS is the right long-term solution.
