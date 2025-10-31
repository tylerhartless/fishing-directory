# Data Pipeline - ETL Scripts

This directory contains Python scripts for extracting, transforming, and loading (ETL) fishing spot data into the MySQL database.

## Setup

1. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure database:**
   ```bash
   cp .env.example .env
   # Edit .env with your Hostinger database credentials
   ```

4. **Test connection:**
   ```bash
   python config.py
   python db_utils.py
   ```

## Available Scripts

### 1. `process_boat_ramps.py`
Processes TPWD boat ramps data.

**Data Source:** https://tpwd.texas.gov/gis/resources/boat-access.phtml

**Usage:**
```bash
# Download CSV from TPWD and save to ../raw-data/tpwd_boat_ramps.csv
python process_boat_ramps.py
```

**Expected CSV Columns:**
- RAMP_NAME (or NAME)
- COUNTY
- WATERBODY (or WATER_BODY)
- LATITUDE (or LAT)
- LONGITUDE (or LON, LONG)
- PARKING (Y/N)
- RESTROOMS (Y/N)
- LIGHTING (Y/N)
- FISH_CLEAN (Y/N)

### 2. `process_state_parks.py`
Imports Texas State Parks with fishing access.

**Usage:**
```bash
python process_state_parks.py
```

### 3. (Future) `process_cfl.py`
Community Fishing Lakes data.

### 4. (Future) `process_raca.py`
River Access (RACA) lease data.

### 5. (Future) `process_habitat_structures.py`
Fish habitat structure coordinates.

## Data Sources

### Official Texas Sources
1. **TPWD Boat Ramps**
   - URL: https://tpwd.texas.gov/gis/resources/boat-access.phtml
   - Format: CSV, Shapefile
   - Update frequency: Annually

2. **Community Fishing Lakes**
   - URL: https://tpwd.texas.gov/fishboat/fish/recreational/lakes/
   - Format: Web scraping or manual entry

3. **RACA (River Access)**
   - URL: https://tpwd.texas.gov/fishboat/fish/recreational/raca/
   - Format: PDF maps, coordinate extraction needed

4. **Fish Habitat Structures**
   - URL: https://tpwd.texas.gov/fishboat/fish/habitats/
   - Format: Various by lake

5. **Texas State Parks**
   - URL: https://tpwd.texas.gov/state-parks/
   - Note: Free fishing, no license required!

## Workflow

1. Download raw data files to `../raw-data/`
2. Run appropriate processing script
3. Verify data in database
4. Check processed output in `../processed-data/`

## Common Issues

**Problem:** `ModuleNotFoundError: No module named 'mysql'`
**Solution:** Make sure you're in the virtual environment and ran `pip install -r requirements.txt`

**Problem:** `Access denied for user`
**Solution:** Check your .env file has correct Hostinger credentials

**Problem:** Duplicate slug errors
**Solution:** The scripts auto-generate unique slugs. Check if you're running the same data twice.

## Adding New Data Sources

To add a new data source:

1. Create a new script: `process_[source_name].py`
2. Follow the template in `process_boat_ramps.py`
3. Use `db_utils.bulk_insert()` for efficient imports
4. Generate unique slugs with `generate_unique_slug()`
5. Set appropriate `data_source` field for tracking

## Pro Tips

- Always keep raw data files in `raw-data/` (not tracked by git)
- Run scripts incrementally (test with small datasets first)
- Use `is_verified=True` for official government data
- Use `is_verified=False` for user submissions
- Generate SEO-friendly meta titles and descriptions during import
