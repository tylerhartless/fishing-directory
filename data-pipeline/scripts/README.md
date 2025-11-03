# Scripts Directory

This directory contains **optional enrichment scripts** for the fishing directory pipeline.

## Current Scripts

### OSM Enrichment (Optional)

**Purpose:** Enhance fishing spot data with amenity information from OpenStreetMap.

#### 1. `enrich_from_osm.py`
Fetches amenity data from OpenStreetMap for fishing spots that need enrichment.

```bash
python scripts/enrich_from_osm.py
```

**What it does:**
- Queries local OSM data (if available) or Overpass API
- Finds nearby amenities (restrooms, parking, etc.)
- Saves results for manual review

#### 2. `apply_osm_enrichment.py`
Applies the enrichment results to the database.

```bash
python scripts/apply_osm_enrichment.py
```

**What it does:**
- Reads enrichment results
- Updates fishing_spots table with amenity data
- Preserves manually-entered data (won't overwrite)

### Usage Workflow

OSM enrichment is **entirely optional** and should be run after all adapters:

```bash
# Step 1: Import all data
cd adapters
python texas_lakes_adapter.py
python texas_state_parks_combined_adapter.py
# ... etc

# Step 2: Apply manual corrections
cd ..
python data_corrections/apply_all_corrections.py

# Step 3 (Optional): Enrich with OSM data
cd scripts
python enrich_from_osm.py
python apply_osm_enrichment.py
```

## Archive Directory

The `archive/` subdirectory contains one-off scripts from development. See [archive/README.md](archive/README.md) for details.

**Do not run archived scripts** - they are for historical reference only. All fixes they applied are documented in `data_corrections/corrections_manifest.json`.

## Core Pipeline Scripts

The reproducible pipeline scripts are located elsewhere:

- **Adapters:** `../adapters/` - Import data from various sources
- **Corrections:** `../data_corrections/` - Apply documented data fixes
- **Database:** `../db_utils.py` - Database utilities
- **ETL Base:** `../etl_base.py` - Base class for all adapters

## Documentation

For complete rebuild instructions, see:
- [PIPELINE_ROBUSTNESS_IMPROVEMENTS.md](../PIPELINE_ROBUSTNESS_IMPROVEMENTS.md)
- [REBUILD_AUDIT.md](../REBUILD_AUDIT.md)
- [IMPORT_WORKFLOW.md](../IMPORT_WORKFLOW.md)

---

**Last Updated:** 2025-11-03
