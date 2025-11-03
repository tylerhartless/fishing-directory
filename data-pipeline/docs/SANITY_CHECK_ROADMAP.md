# Texas Data Sanity Check - Implementation Roadmap

## Goal

Re-process all Texas data through the improved pipeline and compare against current database to validate our data quality rules and ensure we can cleanly reimport data for Texas (and eventually other states).

## Timeline

**Phase 1-2:** ~1 week (infrastructure)
**Phase 3-4:** ~2-3 days (processing)
**Phase 5:** ~1-2 days (review)
**Total:** ~2 weeks to production-ready pipeline

---

## Phase 1: Infrastructure Setup (Days 1-3)

### 1.1 Download Texas OSM Data
```bash
cd data-pipeline/osm/

# Download Texas extract (~500MB)
wget https://download.geofabrik.de/north-america/us/texas-latest.osm.pbf

# Verify download
ls -lh texas-latest.osm.pbf
```

### 1.2 Set Up Local OSM Database (Option A: PostGIS)
```bash
# Create database
createdb fishing_osm

# Enable PostGIS
psql fishing_osm -c "CREATE EXTENSION postgis;"

# Import OSM data
osm2pgsql -c -d fishing_osm \
  --create \
  --slim \
  -G \
  --hstore \
  --style /usr/share/osm2pgsql/default.style \
  texas-latest.osm.pbf

# This takes ~10-15 minutes for Texas
```

**Alternative 1.2: Set Up Local OSM (Option B: Osmium)**
```bash
# If PostGIS is overkill, use Osmium for direct queries
pip install osmium

# Create Python query interface
# (see osm_local_query.py below)
```

### 1.3 Create Staging Directory Structure
```bash
mkdir -p data-pipeline/staged/{raw,enriched,validated,reports,duplicates,current}

# Directory structure:
# staged/
#   raw/          - Raw JSON from each source adapter
#   enriched/     - After OSM enrichment
#   validated/    - After deduplication & validation
#   reports/      - Import and comparison reports
#   duplicates/   - Duplicate candidates for review
#   current/      - Current DB export for comparison
```

### 1.4 Create Export Script
```python
# scripts/export_current_data.py
"""Export current database to JSON for comparison"""

import json
import mysql.connector
from config import DB_CONFIG

conn = mysql.connector.connect(**DB_CONFIG)
cur = conn.cursor(dictionary=True)

cur.execute("""
    SELECT id, name, slug, latitude, longitude, county,
           water_body_name, spot_type, address, description,
           amenities, data_source, state
    FROM fishing_spots
    WHERE state = 'TX'
    ORDER BY id
""")

spots = cur.fetchall()

# Convert to serializable format
for spot in spots:
    if spot['amenities']:
        spot['amenities'] = json.loads(spot['amenities'])

output = {
    'exported_at': datetime.now().isoformat(),
    'total_count': len(spots),
    'spots': spots
}

with open('staged/current/texas_current.json', 'w') as f:
    json.dump(output, f, indent=2)

print(f"Exported {len(spots)} Texas spots")
```

---

## Phase 2: Build Core Pipeline Components (Days 4-5)

### 2.1 Create OSM Local Query Module
```python
# pipeline/osm_local.py
"""Query local OSM database instead of Overpass API"""

import psycopg2
from psycopg2.extras import RealDictCursor

class LocalOSMEnricher:
    def __init__(self):
        self.conn = psycopg2.connect(
            dbname='fishing_osm',
            user='postgres',
            host='localhost'
        )

    def find_water_bodies_near(self, lat, lon, radius_m=500):
        """Find water bodies within radius"""
        query = """
            SELECT
                name,
                way_area,
                ST_Distance(
                    ST_Transform(way, 4326)::geography,
                    ST_SetSRID(ST_MakePoint(%s, %s), 4326)::geography
                ) as distance_meters
            FROM planet_osm_polygon
            WHERE (natural = 'water' OR water IN ('lake', 'pond', 'reservoir'))
              AND name IS NOT NULL
              AND ST_DWithin(
                ST_Transform(way, 4326)::geography,
                ST_SetSRID(ST_MakePoint(%s, %s), 4326)::geography,
                %s
              )
            ORDER BY distance_meters
            LIMIT 5
        """

        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query, (lon, lat, lon, lat, radius_m))
            return cur.fetchall()

    def find_parks_near(self, lat, lon, radius_m=500):
        """Find parks/facilities within radius"""
        query = """
            SELECT
                name,
                leisure,
                ST_Distance(
                    ST_Transform(way, 4326)::geography,
                    ST_SetSRID(ST_MakePoint(%s, %s), 4326)::geography
                ) as distance_meters
            FROM planet_osm_polygon
            WHERE leisure IN ('park', 'nature_reserve')
              AND name IS NOT NULL
              AND ST_DWithin(
                ST_Transform(way, 4326)::geography,
                ST_SetSRID(ST_MakePoint(%s, %s), 4326)::geography,
                %s
              )
            ORDER BY distance_meters
            LIMIT 5
        """

        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query, (lon, lat, lon, lat, radius_m))
            return cur.fetchall()

    def find_amenities_near(self, lat, lon, radius_m=500):
        """Find amenities within radius"""
        query = """
            SELECT
                amenity,
                leisure,
                COUNT(*) as count
            FROM planet_osm_point
            WHERE amenity IN ('parking', 'toilets', 'picnic_site')
               OR leisure IN ('slipway', 'fishing', 'marina')
              AND ST_DWithin(
                ST_Transform(way, 4326)::geography,
                ST_SetSRID(ST_MakePoint(%s, %s), 4326)::geography,
                %s
              )
            GROUP BY amenity, leisure
        """

        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query, (lon, lat, radius_m))
            return cur.fetchall()
```

### 2.2 Create Validation Module
```python
# pipeline/validator.py
"""Data validation and cleaning"""

import re
from typing import Tuple, Optional

class SpotValidator:
    COMBINED_NAME_PATTERNS = [
        r"^(.+?) on (.+)$",
        r"^(.+?) at (.+)$",
        r"^(.+?) - (.+) (Access|Park|Ramp)$",
    ]

    def separate_park_and_water(self, name: str) -> Tuple[str, Optional[str]]:
        """Separate combined park/water names"""

        for pattern in self.COMBINED_NAME_PATTERNS:
            match = re.match(pattern, name)
            if match:
                part1, part2 = match.groups()[:2]

                # Determine which is park vs water
                water_keywords = ['Lake', 'Pond', 'Reservoir', 'River', 'Creek']
                park_keywords = ['Park', 'Access', 'Recreation']

                if any(kw in part2 for kw in water_keywords):
                    return part1.strip(), part2.strip()
                elif any(kw in part1 for kw in water_keywords):
                    return part2.strip(), part1.strip()

        return name, None

    def generate_water_body_fallback(self, facility_name: str, spot_type: str) -> str:
        """Generate fallback water body name"""

        # If facility name contains water words, use it
        water_keywords = ['Lake', 'Pond', 'Reservoir']
        if any(kw in facility_name for kw in water_keywords):
            return facility_name

        # Otherwise use facility + Waters
        if spot_type in ['public_water', 'fishing_pier']:
            return f"{facility_name} Waters"
        elif spot_type == 'river_access':
            return f"{facility_name} River Access"
        else:
            return "Park Waters"

    def validate_coordinates(self, lat: float, lon: float) -> Tuple[bool, Optional[str]]:
        """Validate coordinates are in Texas"""

        if not (25.8 <= lat <= 36.5 and -106.7 <= lon <= -93.5):
            return False, "Coordinates outside Texas bounds"

        return True, None

    def remove_redundant_info(self, name: str) -> str:
        """Remove redundant location info from names"""

        patterns = [
            r"\s*-\s*Texas$",
            r"\s*,\s*TX$",
            r"\s*\([^)]*County[^)]*\)",
            r"\s*-\s*[A-Z][a-z]+\s+County\s*$",
        ]

        cleaned = name
        for pattern in patterns:
            cleaned = re.sub(pattern, '', cleaned)

        return cleaned.strip()
```

### 2.3 Create Comparison Tool
```python
# pipeline/compare_datasets.py
"""Compare current vs new dataset"""

import json
from difflib import SequenceMatcher

def compare_datasets(current_file, new_file, output_file):
    with open(current_file) as f:
        current = json.load(f)['spots']

    with open(new_file) as f:
        new_data = json.load(f)['spots']

    # Index by ID
    current_by_id = {s['id']: s for s in current}
    new_by_id = {s['id']: s for s in new_data}

    report = {
        'summary': {
            'current_count': len(current),
            'new_count': len(new_data),
            'spots_removed': [],
            'spots_added': [],
            'spots_changed': []
        }
    }

    # Find removed
    for id in current_by_id:
        if id not in new_by_id:
            report['summary']['spots_removed'].append({
                'id': id,
                'name': current_by_id[id]['name'],
                'county': current_by_id[id]['county']
            })

    # Find added
    for id in new_by_id:
        if id not in current_by_id:
            report['summary']['spots_added'].append({
                'id': id,
                'name': new_by_id[id]['name'],
                'county': new_by_id[id]['county']
            })

    # Find changed
    for id in current_by_id:
        if id in new_by_id:
            current_spot = current_by_id[id]
            new_spot = new_by_id[id]

            changes = []
            for field in ['name', 'water_body_name', 'address', 'description']:
                if current_spot.get(field) != new_spot.get(field):
                    changes.append({
                        'field': field,
                        'old': current_spot.get(field),
                        'new': new_spot.get(field)
                    })

            if changes:
                report['summary']['spots_changed'].append({
                    'id': id,
                    'name': current_spot['name'],
                    'changes': changes
                })

    with open(output_file, 'w') as f:
        json.dump(report, f, indent=2)

    return report
```

---

## Phase 3: Process All Sources (Days 6-7)

### 3.1 Run All Adapters to Staging
```bash
# Extract all raw data
python adapters/texas_tpwd_adapter.py --output staged/raw/tpwd_boat_ramps.json
python adapters/texas_community_lakes_adapter.py --output staged/raw/community_lakes.json
python adapters/texas_neighborhood_fishin_adapter.py --output staged/raw/neighborhood.json
python adapters/texas_state_parks_combined_adapter.py --output staged/raw/state_parks.json
python adapters/texas_lakes_adapter.py --output staged/raw/large_lakes.json
python adapters/texas_raca_adapter.py --output staged/raw/raca.json

# City PDFs
python scripts/import_city_csv.py "raw-data/Houston PDF.csv" --output staged/raw/houston_pdf.json
python scripts/import_city_csv.py "raw-data/DFW PDF.csv" --output staged/raw/dfw_pdf.json
python scripts/import_city_csv.py "raw-data/Austin PDF.csv" --output staged/raw/austin_pdf.json
python scripts/import_city_csv.py "raw-data/San Antonio PDF.csv" --output staged/raw/sa_pdf.json
```

### 3.2 Enrich with Local OSM
```bash
# Enrich all staged data with local OSM
python pipeline/enrich_all_sources.py \
  --input staged/raw/*.json \
  --output staged/enriched/ \
  --osm-db fishing_osm
```

### 3.3 Validate and Merge
```bash
# Validate, deduplicate, merge
python pipeline/validate_and_merge.py \
  --input staged/enriched/*.json \
  --output staged/validated/texas_new.json \
  --duplicates-output staged/duplicates/texas_duplicates.json
```

---

## Phase 4: Comparison (Day 8)

### 4.1 Export Current Data
```bash
python scripts/export_current_data.py
# Output: staged/current/texas_current.json
```

### 4.2 Run Comparison
```bash
python pipeline/compare_datasets.py \
  --current staged/current/texas_current.json \
  --new staged/validated/texas_new.json \
  --output staged/reports/texas_comparison.json
```

### 4.3 Generate Human-Readable Report
```bash
python pipeline/generate_review_report.py \
  --comparison staged/reports/texas_comparison.json \
  --output staged/reports/texas_review.md
```

---

## Phase 5: Manual Review & Commit (Days 9-10)

### 5.1 Review Reports
```bash
# Read the comparison
cat staged/reports/texas_review.md

# Review duplicates
cat staged/duplicates/texas_duplicates.json

# Spot check random entries
python pipeline/spot_check.py --count 50
```

### 5.2 Address Issues
- Manual review of flagged duplicates
- Verify name separations
- Check water body fallbacks
- Validate any errors

### 5.3 Commit (when satisfied)
```bash
# Backup current database
mysqldump fishing_db > backups/fishing_db_pre_reimport_$(date +%Y%m%d).sql

# Clear Texas data
python pipeline/clear_state_data.py --state TX --confirm

# Import validated data
python pipeline/commit_validated_data.py \
  --input staged/validated/texas_new.json \
  --report staged/reports/texas_commit_report.json
```

---

## Success Metrics

After sanity check, we should see:

- ✅ **~50-60 duplicates removed** (American Legion, Toledo Bend, etc.)
- ✅ **~300-400 name improvements** (Bull Sallas, Lakeside Park, etc.)
- ✅ **~800 water_body separations** (no more "Park on Lake")
- ✅ **Zero null water_body_names** (all have fallbacks)
- ✅ **All descriptions standardized** (short, factual)
- ✅ **OSM enrichment added ~500 addresses**
- ✅ **All coordinates validated**
- ✅ **Source priority applied consistently**

Final count should be ~4,180 spots (from current 4,235 after removing ~55 duplicates).

---

## Key Files Created

```
data-pipeline/
  docs/
    DATA_PIPELINE_ARCHITECTURE.md    ← High-level design
    DATA_QUALITY_RULES.md            ← Validation rules
    SANITY_CHECK_ROADMAP.md          ← This file
  pipeline/
    osm_local.py                     ← Local OSM queries
    validator.py                     ← Data cleaning
    compare_datasets.py              ← Comparison tool
    generate_review_report.py        ← Report generator
  staged/
    raw/                             ← Raw JSON from sources
    enriched/                        ← After OSM
    validated/                       ← After validation
    current/                         ← Current DB export
    reports/                         ← Comparison reports
```
