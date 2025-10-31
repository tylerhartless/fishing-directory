# Texas Data Acquisition Plan

This document tracks all Texas fishing data sources, acquisition status, and update procedures.

## Overview

**Goal:** Acquire all available Texas fishing access data (~4,000+ spots)

**Priority:** Test new ETL pipeline with diverse data formats before nationwide expansion

## Data Sources Status

### ✅ Completed

| Source | Records | File | Adapter | Last Updated |
|--------|---------|------|---------|--------------|
| TPWD Boat Ramps | 2,234 | `tpwd_boat_ramps.csv` | `TexasTPWDAdapter` | 2025-10-30 |

### 🔄 In Progress

| Source | Est. Records | Priority | Status |
|--------|--------------|----------|--------|
| - | - | - | - |

### 📋 To Acquire

| Source | Est. Records | Priority | Data Format | Notes |
|--------|--------------|----------|-------------|-------|
| Texas State Parks | 75 | HIGH | Manual/Scrape | FREE fishing - unique content |
| Community Fishing Lakes (CFL) | 40 | HIGH | Manual/Scrape | Urban areas, good access |
| RACA River Access | 200 | MEDIUM | PDF/Manual | Requires geocoding |
| Fish Habitat Structures | 1,000+ | MEDIUM | CSV per lake | Start with Lake Fork, Sam Rayburn |
| Fishing Piers | 100 | LOW | Mixed | Some in boat ramp data |
| Coastal Wade Fishing | 100 | LOW | Manual | Gulf coast specific |

## Acquisition Details

### 1. TPWD Boat Ramps ✅

**Status:** Complete
**Records Imported:** 2,234
**Data Quality:** Excellent

**Source:**
- URL: https://tpwd.texas.gov/gis/resources/boat-access.phtml
- File: `raw-data/tpwd_boat_ramps.csv`
- Format: CSV with TPWAID, Latitude, Longitude, AccessTypeDescription

**Adapter:** `adapters/texas_tpwd_adapter.py`

**Update Procedure:**
1. Visit https://tpwd.texas.gov/gis/resources/boat-access.phtml
2. Download latest CSV (check quarterly)
3. Save as `raw-data/tpwd_boat_ramps_YYYY-MM-DD.csv`
4. Run: `python adapters/texas_tpwd_adapter.py`
5. Script will update existing records based on TPWAID

**Next Update Due:** 2026-01-30 (quarterly)

---

### 2. Texas State Parks 📋

**Status:** To Acquire
**Est. Records:** 75 parks
**Priority:** HIGH

**Why Important:**
- Unique content angle: FREE fishing (no license required at state parks)
- High-quality amenities (camping, restrooms, etc.)
- Good for SEO: "free fishing near me"

**Source:**
- URL: https://tpwd.texas.gov/state-parks/parks/find-a-park
- Method: Manual collection or web scraping

**Data Needed Per Park:**
- Park name
- County
- GPS coordinates (get from park detail pages)
- Water bodies (lakes/rivers in park)
- Amenities (camping, pier, boat ramp, etc.)
- Fishing species available
- Park entrance fee
- Contact info

**Acquisition Steps:**
1. Visit state parks website
2. Filter for parks with "fishing" amenity
3. For each park, visit detail page
4. Extract coordinates, water bodies, amenities
5. Save to CSV: `raw-data/texas_state_parks.csv`

**CSV Format:**
```csv
name,county,latitude,longitude,water_body,amenities,entrance_fee,fishing_species,notes
Brazos Bend State Park,Fort Bend,29.3611,-95.5964,Park Lakes,"camping,restrooms,pier,fish_cleaning",8.00,"bass,catfish,sunfish",Excellent fishing year-round
```

**Adapter:** Use `GenericCSVAdapter` or create `TexasStateParksAdapter`

**Update Frequency:** Annually (parks don't change often)

---

### 3. Community Fishing Lakes (CFL) 📋

**Status:** To Acquire
**Est. Records:** 40-50 lakes
**Priority:** HIGH

**Why Important:**
- Urban fishing access
- Stocked by TPWD (always have fish)
- Often have easy bank access
- Great for families and beginners

**Source:**
- URL: https://tpwd.texas.gov/fishboat/fish/recreational/lakes/
- Look for "Community Fishing Lakes" section
- Each lake has detail page with coordinates

**Example Lakes:**
- Lake Pflugerville (Austin)
- Tom Bass Park (Houston)
- Chisholm Park Pond (Killeen)
- Heritage Park (Corpus Christi)

**Data to Collect:**
- Lake name
- City/County
- GPS coordinates
- Size (acres)
- Stocking schedule
- Amenities
- Access type (bank, pier, boat)

**Acquisition Method:**

**Option A: Manual (Fastest)**
1. Create Google Sheet with columns above
2. Visit each lake page
3. Copy data
4. Export to CSV

**Option B: Web Scraping**
```python
# Create scraper with BeautifulSoup
# Parse lake detail pages
# Extract coordinates and amenities
# Export to CSV
```

**CSV Format:**
```csv
name,city,county,latitude,longitude,acres,amenities,stocking_schedule,access_type
Lake Pflugerville,Pflugerville,Travis,30.4516,-97.6020,180,"parking,restrooms,pier,fish_cleaning",Monthly,"bank,pier"
```

**Update Frequency:** Annually

---

### 4. RACA River Access 📋

**Status:** To Acquire
**Est. Records:** 200+ access points
**Priority:** MEDIUM

**Why Important:**
- River fishing is popular in Texas
- Public access on private land (unique program)
- Good content: "where to access [river name]"

**Source:**
- URL: https://tpwd.texas.gov/fishboat/fish/recreational/raca/
- Data Format: PDF maps per river system
- Requires: Geocoding addresses or map coordinates

**Rivers with RACA:**
- Guadalupe River
- Llano River
- San Marcos River
- Colorado River
- Devils River
- Brazos River

**Challenge:** Data is in PDF maps, not CSV

**Acquisition Options:**

**Option A: Email TPWD**
```
Subject: RACA Access Point Coordinates Request

Hello,

I'm building a public fishing directory. Do you have a spreadsheet
or GIS data for RACA access points with GPS coordinates?

Currently data is in PDF format on your website. A CSV or shapefile
would be very helpful.

Thank you!
```

**Option B: Manual from PDFs**
1. Download PDF maps for each river
2. Extract access point names and addresses
3. Use Mapbox/Google Geocoding API to get coordinates
4. Save to CSV

**CSV Format:**
```csv
name,river,county,latitude,longitude,address,landowner,lease_status
Sattler Bridge Access,Guadalupe River,Comal,29.7592,-98.1858,"FM 306 near Sattler, TX",Private lease through RACA,Active
```

**Update Frequency:** Annually (leases don't change often)

---

### 5. Fish Habitat Structures 📋

**Status:** To Acquire
**Est. Records:** 1,000+
**Priority:** MEDIUM

**Why Important:**
- Hardcore anglers love this data
- Great for bass fishing content
- GPS coordinates for "secret" fishing spots
- Good for "where to catch bass in [lake name]"

**Source:**
- URL: https://tpwd.texas.gov/fishboat/fish/habitats/
- Format: Varies by lake (some CSV, some PDF)

**Priority Lakes to Start:**
1. Lake Fork (famous bass lake)
2. Lake Sam Rayburn
3. Toledo Bend
4. Lake Texoma
5. Choke Canyon Reservoir

**Data Per Structure:**
- Structure ID
- Lake name
- GPS coordinates (lat/long)
- Structure type (brush pile, tire reef, etc.)
- Depth
- Installation date
- Status (active, removed, etc.)

**Acquisition:**
1. Visit habitat page for each priority lake
2. Look for downloadable coordinates
3. If PDF only, extract coordinates manually or with PDF scraper
4. Save to: `raw-data/habitat_structures_[lake_name].csv`

**CSV Format:**
```csv
structure_id,lake,county,latitude,longitude,structure_type,depth_ft,installed_date,status
LF001,Lake Fork,Wood,32.7503,-95.4123,Brush pile,15,2023-05-01,Active
```

**Adapter:** Create `HabitatStructuresAdapter`

**Update Frequency:** Annually

---

### 6. Fishing Piers 📋

**Status:** To Acquire
**Est. Records:** 100
**Priority:** LOW

**Why Important:**
- Accessible fishing (often ADA compliant)
- Lighted piers for night fishing
- Good family fishing spots

**Source:**
- Mixed: Some in boat ramp data
- Coastal: https://tpwd.texas.gov/fishboat/fish/recreational/coastal/
- Lakes: Scattered in various datasets

**Acquisition:**
1. Extract piers from existing boat ramp data
2. Add coastal piers from website
3. Research major lake piers

**May overlap with boat ramps - dedupe by coordinates**

---

### 7. Coastal Wade Fishing Access 📋

**Status:** To Acquire
**Est. Records:** 100+
**Priority:** LOW

**Why Important:**
- Gulf coast is huge fishing destination
- Wade fishing is popular technique
- Unique content for saltwater anglers

**Source:**
- URL: https://tpwd.texas.gov/fishboat/fish/recreational/coastal/
- Padre Island National Seashore access
- Galveston Bay areas
- Corpus Christi area

**Data to Collect:**
- Access point name
- County
- GPS coordinates
- Beach/bay
- Parking availability
- Fishing species (speckled trout, redfish, etc.)

---

## Acquisition Workflow

### Step 1: Download/Collect Data
```bash
cd raw-data

# Create dated folder for this acquisition batch
mkdir 2025-11-01-acquisition
cd 2025-11-01-acquisition

# Download or save files here
# Name format: source_name_YYYY-MM-DD.csv
```

### Step 2: Inspect Data
```bash
cd data-pipeline
python check_csv_columns.py ../raw-data/2025-11-01-acquisition/new_dataset.csv
```

### Step 3: Create/Configure Adapter
- Use GenericCSVAdapter with column mapping, OR
- Create custom adapter in `adapters/`

### Step 4: Test Import (Small Sample)
```python
# Test with first 10 rows
df = pd.read_csv('data.csv')
df_sample = df.head(10)
df_sample.to_csv('data_sample.csv')

adapter.process_and_import('data_sample.csv')
```

### Step 5: Verify in Database
```sql
SELECT * FROM fishing_spots
WHERE data_source = 'New_Source_Name'
LIMIT 10;
```

### Step 6: Full Import
```python
adapter.process_and_import('full_dataset.csv')
```

### Step 7: Update Tracking
```sql
UPDATE data_sources
SET last_updated = NOW(),
    record_count = (SELECT COUNT(*) FROM fishing_spots WHERE data_source = 'Source_Name')
WHERE source_name = 'Source_Name';
```

---

## Data Quality Checklist

Before importing any dataset:

- [ ] Valid GPS coordinates (not 0,0 or null)
- [ ] County names match Texas counties
- [ ] Water body names are consistent
- [ ] No duplicate records (check by name + coordinates)
- [ ] Amenities data is structured
- [ ] Source is documented for attribution

---

## Update Strategy

### Quarterly Updates (Boat Ramps)
1. Download latest TPWD boat ramp data
2. Compare record counts
3. Run update script (not full re-import)
4. Update `last_updated` in data_sources

### Annual Reviews (All Sources)
- Check each source URL for changes
- Re-download and compare
- Update as needed

### Programmatic Updates

**Goal:** Create update scripts that can refresh data without manual intervention

**Requirements:**
1. Track source_record_id for matching
2. Compare new data to existing
3. Update changed records
4. Add new records
5. Mark removed records as inactive

**Future Tool:** Create `update_from_source.py` script

---

## Next Steps (Priority Order)

1. **Sanity Check Current Data** ✓
   - Verify 2,234 boat ramps are in database
   - Spot-check coordinates on map
   - Check for any data quality issues

2. **State Parks (Quick Win)**
   - Manually collect 10-20 major parks
   - Test GenericCSVAdapter
   - Full import if successful

3. **Community Fishing Lakes**
   - Scrape or manual collection
   - ~40 lakes, manageable dataset
   - Test web scraping approach

4. **RACA River Access**
   - Email TPWD for data
   - Or manual extraction from PDFs
   - Test geocoding workflow

5. **Fish Habitat Structures**
   - Start with Lake Fork only
   - Validate structure data format
   - Expand to other lakes if successful

---

## Questions to Resolve

1. **RACA Data:** Should we email TPWD first or manually extract from PDFs?
2. **State Parks:** Manual collection or invest time in scraper?
3. **Habitat Structures:** Include all or just popular lakes?
4. **Update Strategy:** Build update scripts now or after all data acquired?

---

## Resources

- TPWD GIS Contact: gisdata@tpwd.texas.gov
- Mapbox Geocoding API: https://docs.mapbox.com/api/search/geocoding/
- Texas Counties List: https://en.wikipedia.org/wiki/List_of_counties_in_Texas

---

Last Updated: 2025-10-31
