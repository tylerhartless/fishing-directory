# Database Rebuild Audit

## Problem Statement
If the database is lost, can we rebuild it accurately from raw data using only the ETL pipeline?

**Short Answer**: Not yet. Many manual fixes and consolidations were done via one-off scripts that are not integrated into the automated adapters.

---

## Current Pipeline State

### Automated Adapters (✅ Can be re-run)
Located in `data-pipeline/adapters/`:

1. **texas_lakes_adapter.py** - Major lakes from TPWD
2. **texas_community_lakes_adapter.py** - Community fishing lakes
3. **texas_neighborhood_fishin_adapter.py** - Neighborhood Fishin' program
4. **texas_raca_adapter.py** - River Access and Conservation Areas
5. **texas_state_parks_combined_adapter.py** - State parks with fishing
6. **texas_state_parks_poi_adapter.py** - State park POIs
7. **texas_tpwd_adapter.py** - TPWD official data
8. **texas_city_pdf_adapter.py** - City fishing guide PDFs

### ETL Base Deduplication (✅ Automated)
File: `data-pipeline/etl_base.py`

**Hierarchy implemented** (lines 127-193):
- Lakes coexist with state parks ✅
- State parks consolidate public_water ✅
- Boat ramps stay separate ✅
- Same type consolidates ✅
- 100m proximity threshold ✅

---

## Manual Fixes NOT in Pipeline

### 1. ❌ Sheldon Lake Consolidation
**Script**: `scripts/consolidate_sheldon.py`
**What it did**:
- Set ID 3254 as parent (Sheldon Lake State Park)
- Linked 5 children (Children's ponds, "Sheldon")
- Deleted 2 duplicates (ID 800, ID 3171)
- Updated spot_type to 'state_park'

**Problem**:
- The Texas State Parks adapter creates the main entry correctly
- BUT the dedup logic didn't catch "Lake Sheldon" as duplicate
- Manual deletion of duplicates not reproducible

**Solution Needed**:
- Add to `data_corrections/sheldon_lake_fix.py` as permanent correction
- OR improve name similarity matching in ETL base

---

### 2. ❌ Numbered Pond Consolidations (18 groups)
**Script**: `scripts/consolidate_numbered_ponds.py`
**What it did**:
- Created 18 parent entries for pond groups
- Linked 44 children (numbered ponds)

**Groups**:
```python
- Bates Allen Park (2 ponds)
- Davidson Creek (2 ponds)
- Evergreen Pond (3 ponds)
- Hackberry Park (5 ponds)
- Jones Lake (3 ponds)
- Willow Waterhole Units (4 ponds)
# ... 12 more groups
```

**Problem**:
- These are real numbered ponds in the source data
- Pipeline will re-import them as separate entries
- Consolidation logic doesn't automatically detect numbered patterns

**Solution Needed**:
- Add numbered pond detection to ETL base class
- Pattern: `r'(.+?)\s+(Pond\s+)?#?\d+$'`
- Auto-create parent if 2+ within 1000m

---

### 3. ❌ HTML Entity Decoding
**Script**: `scripts/fix_frontend_bugs.py`
**What it did**:
- Fixed 11 spot names with HTML entities
- "Children&#39;s" → "Children's"
- "Lion&#39;s" → "Lion's"

**Problem**:
- Source data has double-encoded HTML entities
- Re-import will re-introduce the issue

**Solution Needed**:
- Add HTML entity decoding to ETL base `clean_name()` method
```python
import html
name = html.unescape(html.unescape(name))
```

---

### 4. ❌ Name Corrections
**Scripts**: Multiple one-off fixes
- `fix_addicks.py` - "Addicks" → "Bear Creek Pioneers Park"
- `fix_issues.py` - "Nassau" → "Nassau Bay"
- `consolidate_raven.py` - Deleted duplicate "Raven" (kept "Lake Raven")
- `fix_issues.py` - Deleted duplicate Hackberry Park (NULL water body)

**Problem**:
- These corrections are based on local knowledge
- Source data still has incorrect names
- Re-import will bring back incorrect data

**Solution Needed**:
- Centralized corrections file: `data_corrections/name_fixes.json`
```json
{
  "texas_community_lakes": {
    "Addicks": {
      "correct_name": "Bear Creek Pioneers Park",
      "reason": "Coordinates point to park, not reservoir"
    },
    "Nassau": {
      "correct_name": "Nassau Bay",
      "reason": "Incomplete name"
    }
  }
}
```

---

### 5. ❌ Duplicate Deletions
**Scripts**: Multiple
- `consolidate_raven.py` - Deleted ID 2959 (Raven duplicate)
- `fix_issues.py` - Deleted ID 3281 (Hackberry duplicate)
- `consolidate_sheldon.py` - Deleted ID 800, 3171

**Problem**:
- Dedup logic didn't catch these
- Distance-based (0-60m apart) but different sources

**Solution Needed**:
- Improve dedup to catch exact coordinate matches
- Lower threshold for lake/public_water conflicts
- Source priority: Official > Manual > Community > City PDFs

---

### 6. ✅ OSM Enrichment (Partially automated)
**Scripts**:
- `scripts/enrich_from_osm.py` (dry-run)
- `scripts/apply_osm_enrichment.py` (apply)

**Status**: Can be re-run, but requires manual trigger
**Result**: 495 spots enriched with amenity data

**Solution**: This is acceptable - enrichment is bonus data

---

### 7. ❌ Parent-Child Relationships
**Problem**: Many parent-child relationships were manually created:
- Sheldon Lake complex
- 18 pond groups
- Willow Waterhole units

**Dedup logic only prevents duplicates, doesn't create parent-child**

**Solution Needed**:
- Add parent-child creation to ETL base
- When duplicate detected, create relationship instead of skipping

---

## Raw Data Inventory

### ✅ Complete Sources (can rebuild)
```
raw-data/
├── texas_major_lakes.json          # Lakes adapter ✅
├── texas_community_lakes.json      # Community lakes adapter ✅
├── texas_neighborhood_fishin.json  # Neighborhood adapter ✅
├── texas_raca.json                 # RACA adapter ✅
├── texas_state_parks.json          # State parks adapter ✅
├── austin_fishing.pdf              # City PDF adapter ✅
├── dfw_fishing.pdf                 # City PDF adapter ✅
├── houston_fishing.pdf             # City PDF adapter ✅
└── san_antonio_fishing.pdf         # City PDF adapter ✅
```

### ❌ Missing from Pipeline
- Manual consolidations (not in raw data)
- Name corrections (based on local knowledge)
- OSM enrichment results (external API, can re-run)

---

## Rebuild Test Plan

### Step 1: Backup Current Database
```bash
docker exec fishing-db mysqldump -u root -proot fishing_db > backup_$(date +%Y%m%d).sql
```

### Step 2: Drop and Recreate Database
```bash
docker exec fishing-db mysql -u root -proot -e "DROP DATABASE fishing_db; CREATE DATABASE fishing_db;"
docker exec fishing-db mysql -u root -proot fishing_db < database/schema.sql
```

### Step 3: Run All Adapters
```bash
cd data-pipeline/adapters
python texas_lakes_adapter.py
python texas_community_lakes_adapter.py
python texas_neighborhood_fishin_adapter.py
python texas_raca_adapter.py
python texas_state_parks_combined_adapter.py
python texas_city_pdf_adapter.py
```

### Step 4: Compare Results
```sql
-- Count spots by type
SELECT spot_type, COUNT(*) FROM fishing_spots GROUP BY spot_type;

-- Check for duplicates
SELECT name, county, COUNT(*) as count
FROM fishing_spots
GROUP BY name, county
HAVING count > 1;

-- Check parent-child relationships
SELECT COUNT(*) FROM fishing_spots WHERE is_parent = TRUE;
SELECT COUNT(*) FROM fishing_spots WHERE parent_spot_id IS NOT NULL;
```

### Step 5: Apply Corrections
```bash
# Run correction scripts in order
python data_corrections/apply_all_corrections.py
```

---

## Recommendations

### Priority 1: Integrate into ETL Base
1. **HTML entity decoding** in `clean_name()` method
2. **Numbered pond detection** with auto-parent creation
3. **Exact coordinate duplicate detection** (< 10m threshold)
4. **Parent-child relationship creation** when dedup triggered

### Priority 2: Create Corrections Framework
```
data-pipeline/data_corrections/
├── name_fixes.json              # Source-specific name corrections
├── deletions.json               # Known duplicates to delete
├── consolidations.json          # Parent-child relationships
└── apply_all_corrections.py     # Master script
```

### Priority 3: Document Manual Steps
Create `REBUILD_PROCEDURE.md` with:
1. Order to run adapters
2. Required correction scripts
3. Enrichment steps (OSM, geocoding)
4. Verification queries

### Priority 4: Automated Testing
Create `scripts/test_rebuild.py`:
- Runs full rebuild in test DB
- Compares counts to production
- Verifies no regressions
- Runs weekly via cron

---

## Gap Analysis Summary

| Fix Type | Count | Automated? | Risk if Lost |
|----------|-------|------------|--------------|
| HTML entities | 11 | ❌ | Medium - cosmetic |
| Numbered ponds | 18 groups (44 children) | ❌ | High - UX clutter |
| Name corrections | 4 | ❌ | Medium - accuracy |
| Duplicate deletions | 5 | ❌ | Medium - data quality |
| Parent-child links | ~50 total | ❌ | High - UX clutter |
| Sheldon consolidation | 1 complex | ❌ | High - 9 entries → 1 |
| OSM enrichment | 495 spots | ⚠️ Manual | Low - bonus data |

**Total manual fixes**: ~120 database modifications not reproducible from pipeline

---

## Next Steps

1. ✅ Create this audit document
2. ⏳ Build corrections framework
3. ⏳ Enhance ETL base class with missing logic
4. ⏳ Test full rebuild
5. ⏳ Document rebuild procedure
6. ⏳ Set up automated testing
