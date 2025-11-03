# OSM Import Instructions

## File Ready
✅ **us-south-251101.osm.pbf** (3.7 GB)
- Downloaded: November 2, 2025
- Coverage: Texas to Florida, up to Carolinas
- 14 states total

## When You're Ready to Import

### Option 1: PostGIS (Recommended)

**Prerequisites:**
- PostgreSQL with PostGIS extension
- At least 20-25 GB free disk space
- 4+ GB RAM available

**Steps:**

```bash
# 1. Create database
createdb fishing_osm

# 2. Enable PostGIS
psql fishing_osm -c "CREATE EXTENSION postgis;"
psql fishing_osm -c "CREATE EXTENSION hstore;"

# 3. Import OSM data (this takes 30-45 minutes)
cd c:\Users\tyash\Desktop\fishing-directory\data-pipeline\osm

osm2pgsql -c -d fishing_osm \
  --create \
  --slim \
  -G \
  --hstore \
  --multi-geometry \
  --number-processes 4 \
  --cache 4096 \
  us-south-251101.osm.pbf

# Watch the progress - it will show:
# - Reading ways
# - Processing nodes
# - Processing relations
# - Creating indexes

# 4. Verify import
psql fishing_osm -c "\dt"
# Should see: planet_osm_point, planet_osm_line, planet_osm_polygon, planet_osm_roads

# 5. Check Texas water bodies count
psql fishing_osm -c "
  SELECT COUNT(*)
  FROM planet_osm_polygon
  WHERE (natural = 'water' OR water IN ('lake', 'pond', 'reservoir'))
    AND name IS NOT NULL
    AND ST_Contains(
      ST_MakeEnvelope(-106.65, 25.84, -93.51, 36.50, 4326),
      ST_Transform(way, 4326)
    );
"
# Should show thousands of named water bodies in Texas

# 6. Run coverage analysis
cd c:\Users\tyash\Desktop\fishing-directory\data-pipeline\scripts
python analyze_osm_coverage.py
```

### Option 2: Osmium (Lighter Alternative)

If you don't want to set up PostgreSQL:

```bash
# Install osmium
pip install osmium

# No import needed - query PBF file directly!
# See docs/OSM_SETUP_GUIDE.md for usage examples
```

## Next Steps After Import

1. **Test queries** - Try finding water bodies at known Texas coordinates
2. **Run coverage analysis** - See which states have best data
3. **Update enrichment scripts** - Switch from Overpass API to local DB
4. **Benchmark speed** - Should be 100x faster than API calls

## Storage Usage

After import you'll have:
- PBF file: 3.7 GB
- PostGIS database: ~15-20 GB
- Total: ~20-25 GB

You can delete the PBF file after import if you need space (can re-download later).

## Troubleshooting

### osm2pgsql not found
```bash
# Install osm2pgsql
# Ubuntu/Debian:
sudo apt install osm2pgsql

# macOS:
brew install osm2pgsql

# Windows:
# Download from https://github.com/openstreetmap/osm2pgsql/releases
```

### Out of memory
```bash
# Reduce cache size
osm2pgsql --cache 2048 us-south-251101.osm.pbf
```

### Import taking too long
This is normal! 3.7 GB takes 30-45 minutes. You can:
- Let it run overnight
- Use fewer processes: `--number-processes 2`
- Monitor progress in the terminal

## Quick Test After Import

```sql
-- Find water bodies near Houston
psql fishing_osm

SELECT
    name,
    water,
    ST_Distance(
        ST_Transform(way, 4326)::geography,
        ST_SetSRID(ST_MakePoint(-95.3698, 29.7604), 4326)::geography
    ) / 1000.0 as distance_km
FROM planet_osm_polygon
WHERE (natural = 'water' OR water IN ('lake', 'pond'))
  AND name IS NOT NULL
  AND ST_DWithin(
    ST_Transform(way, 4326)::geography,
    ST_SetSRID(ST_MakePoint(-95.3698, 29.7604), 4326)::geography,
    5000
  )
ORDER BY distance_km
LIMIT 10;
```

## Re-Importing (Future Updates)

OSM data changes monthly. To update:

```bash
# Download latest
cd data-pipeline/osm
wget -N https://download.geofabrik.de/north-america/us-south-latest.osm.pbf

# Drop old database
dropdb fishing_osm

# Re-import
createdb fishing_osm
psql fishing_osm -c "CREATE EXTENSION postgis;"
psql fishing_osm -c "CREATE EXTENSION hstore;"
osm2pgsql -c -d fishing_osm --create --slim -G --hstore us-south-latest.osm.pbf
```
