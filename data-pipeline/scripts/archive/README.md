# Archived Scripts

This directory contains one-off scripts that were used during development and initial data cleanup. These scripts are **not part of the reproducible pipeline** and are kept for historical reference only.

## Why These Were Archived

All manual fixes and data corrections documented in these scripts have been:
1. Applied to the production database
2. Added to `data_corrections/corrections_manifest.json` for reproducibility
3. Documented in pipeline improvement documentation

## Script Categories

### One-Off Data Fixes
Scripts that fixed specific data quality issues:
- `fix_*.py` - Various name, county, and data corrections
- `consolidate_*.py` - Merged duplicate entries
- `cleanup_*.py` - Description and formatting fixes

### Import Scripts (Replaced by Adapters)
Old import scripts replaced by the adapter framework:
- `import_austin_csv.py`
- `import_city_csv.py`
- `scrape_*.py`
- Legacy processing scripts

### Analysis & Verification Scripts
One-time analysis that informed pipeline improvements:
- `check_*.py` - Data quality checks
- `find_*.py` - Duplicate detection
- `analyze_*.py` - OSM coverage analysis
- `verify_*.py` - Validation scripts

### OSM Enrichment Experiments
Various approaches to OSM enrichment (consolidated into main scripts):
- `enrich_*.py` - Different enrichment strategies
- `compare_*.py` - OSM data comparison
- `bulk_*.py` - Batch processing experiments

### Database Migrations (Replaced)
Old migration runners (now use standard migration system):
- `run_migration_*.py`
- `run_parent_child_migration.py`

### Utility Scripts (Deprecated)
- `apply_corrections.py` - Replaced by `data_corrections/apply_all_corrections.py`
- `reverse_geocode.py` - One-time geocoding (results now in corrections manifest)
- `show_*.py` - Display/summary scripts for development

## Current Pipeline (Active Scripts)

For the reproducible pipeline, use:

**Data Import:**
- `adapters/*.py` - State-specific data adapters

**Manual Corrections:**
- `data_corrections/apply_all_corrections.py` - Apply all documented fixes

**Optional Enrichment:**
- `scripts/enrich_from_osm.py` - Fetch OSM amenity data
- `scripts/apply_osm_enrichment.py` - Apply OSM enrichment to database

**Documentation:**
- See `PIPELINE_ROBUSTNESS_IMPROVEMENTS.md` for rebuild procedure
- See `REBUILD_AUDIT.md` for gap analysis

## If Database is Lost

**Do NOT run these archived scripts!** Instead:

1. Run all adapters in `adapters/` directory
2. Run `data_corrections/apply_all_corrections.py`
3. Optionally run OSM enrichment scripts

This will reproduce the current database state accurately.

---

**Last Updated:** 2025-11-03
**Archive Purpose:** Historical reference and audit trail
