# Repository Cleanup Plan

## Files to Delete

### data-pipeline/ (root)
- `=3.6.0` - Erroneous pip file
- `check_csv_columns.py` - One-off inspection script
- `inspect_csvs.py` - One-off inspection script
- `process_boat_ramps.py` - Replaced by adapter system
- `process_state_parks.py` - Replaced by adapter system

### data-pipeline/scripts/
**One-off/Temporary Scripts:**
- `check_city_import.py` - Temporary check
- `check_state_parks.py` - Temporary check
- `check_lake_houston_park.py` - Temporary check
- `test_geocode.py` - Temporary test
- `test_osm_enrichment.py` - Temporary test
- `test_raca_enrichment.py` - Temporary test
- `fix_name_spaces.py` - One-time fix (already applied)
- `trim_spot_names.py` - One-time fix (already applied)
- `convert_cfl_to_json.py` - One-time conversion (already applied)
- `update_lake_dabney.py` - One-time update (already applied)

**Parsing Scripts (Specific to one-time data imports):**
- `parse_houston_pdf.py` - Specific to Houston PDF (superseded by parse_city_fishing_pdfs.py)
- `parse_city_fishing_pdfs.py` - User prefers manual entry now
- `scrape_neighborhood_fishin.py` - One-time scrape (data already imported)

### raw-data/
**Temporary/Intermediate Files:**
- `nul` - Empty error file
- `test_scrape.json` - Test file
- `houston_pdf_text.txt` - Intermediate parsing output
- `houston_fishing_spots.json` - Intermediate file (superseded by all_city_fishing_spots.json)

**Redundant Parsed Files (Data already in DB):**
- `cfl.js` - Original CFL data (converted to community_fishing_lakes.json)
- `neighborhood_fishin_lakes.json` - Data already in DB
- `community_fishing_lakes.json` - Data already in DB
- `texas_lakes.json` - Data already in DB

## Files to Keep

### data-pipeline/scripts/ (Utility Scripts)
- `show_database_summary.py` - Useful for DB inspection
- `reverse_geocode.py` - Reusable geocoding utility
- `enrich_state_parks.py` - Reusable for future updates
- `enrich_raca_amenities.py` - Reusable for RACA updates
- `apply_corrections.py` - Reusable for data corrections
- `osm_enrichment_summary.py` - Useful for checking enrichment
- `show_enrichment_results.py` - Useful for checking enrichment
- `show_enrichment_stats.py` - Useful for stats
- `bulk_enrich_osm.py` - Reusable OSM enrichment tool
- `enrich_from_osm.py` - Reusable OSM enrichment tool
- `verify_lake_names_osm.py` - Useful verification tool
- `scrape_leaflet_geojson.py` - Generic scraper, potentially reusable

### raw-data/ (Source Data - Keep)
- PDFs (austin_fishing.pdf, dfw_fishing.pdf, houston_fishing.pdf, san_antonio_fishing.pdf)
- CSV files from TPWD (tpwd_boat_ramps.csv, Point_of_Interest.csv, etc.)
- RACA files
- `all_city_fishing_spots.json` - Master parsed city data

## Recommended Actions

1. **Create archive folder** for one-time scripts: `data-pipeline/scripts/archive/`
2. **Move (don't delete)** one-off scripts to archive folder
3. **Delete** truly temporary files (nul, test files, intermediate outputs)
4. **Add .gitignore entries** to prevent future clutter:
   - `*.pyc`
   - `__pycache__/`
   - `nul`
   - `*.log`
   - Test output files

## Summary
- **Delete immediately**: 5 files (nul, test files, erroneous files)
- **Archive**: 16 scripts (one-off/temporary)
- **Keep**: 11 utility scripts, all source data files
