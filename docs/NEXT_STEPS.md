# Next Steps - Data Acquisition Phase

## Current Status ✅

**Infrastructure:** Complete and tested
- ✅ Scalable ETL framework with adapter pattern
- ✅ Docker development environment
- ✅ Database schema with source tracking
- ✅ Frontend with working search (2,234 spots)

**Data Imported:**
- ✅ TPWD Boat Ramps: 2,234 records

**Remaining Texas Data:** ~2,000 additional spots to acquire

## Your Action Items 🎯

### 1. Run Database Migration (5 minutes)

Before starting data acquisition, add source tracking:

```bash
# Start Docker if not running
docker compose up -d

# Run migration
docker exec -i fishing_directory_db mysql -u fishing_user -pfishing_pass fishing_directory < data-pipeline/migrations/002_add_data_source_tracking.sql
```

This creates the `data_sources` table to track update schedules.

### 2. Gather Texas State Parks Data (1-2 hours)

**Priority:** HIGH - Unique content angle (free fishing!)

**Steps:**
1. Visit: https://tpwd.texas.gov/state-parks/parks/find-a-park
2. Create CSV with these columns:
   ```
   name,county,latitude,longitude,water_body,entrance_fee,fishing_species,notes
   ```
3. For each park with fishing:
   - Copy coordinates from park detail page
   - Note water bodies available
   - List fishing species
   - Add note about FREE fishing (no license required)

**Target:** 10-20 major parks to start (Brazos Bend, Inks Lake, etc.)

**Save as:** `raw-data/texas_state_parks.csv`

**Import with:**
```python
from adapters import GenericCSVAdapter

column_map = {
    'name': 'name',
    'latitude': 'latitude',
    'longitude': 'longitude',
    'county': 'county',
    'water_body': 'water_body'
}

adapter = GenericCSVAdapter("Texas_State_Parks", "TX", column_map)
adapter.process_and_import('raw-data/texas_state_parks.csv')
```

### 3. Gather Community Fishing Lakes (1-2 hours)

**Priority:** HIGH - Urban fishing, stocked by TPWD

**Steps:**
1. Visit: https://tpwd.texas.gov/fishboat/fish/recreational/lakes/
2. Find "Community Fishing Lakes" section
3. For each lake, visit detail page and collect:
   - Name, city, county
   - GPS coordinates
   - Size (acres)
   - Amenities
   - Stocking schedule

**Target:** ~40 lakes

**Save as:** `raw-data/tpwd_community_lakes.csv`

### 4. Check for Updated Boat Ramp Data (5 minutes)

**URL:** https://tpwd.texas.gov/gis/resources/boat-access.phtml

**Check:**
- Is there a direct download link now?
- Has the data been updated since you last downloaded?
- What's the file date on their CSV?

**If newer data exists:**
- Download as `raw-data/tpwd_boat_ramps_YYYY-MM-DD.csv`
- We'll need to create an update script (not full re-import)

### 5. Email TPWD for RACA Data (5 minutes)

**To:** gisdata@tpwd.texas.gov

**Subject:** Public Data Request - RACA Access Point Coordinates

**Body:**
```
Hello,

I'm building a public fishing access directory to help Texas anglers
find fishing spots more easily. I'm looking for geographic data on
RACA (River Access) points including:

- Access point names and locations
- GPS coordinates (latitude/longitude)
- River/stream names
- County information

Currently this data appears to be in PDF maps on your website.
Would you have this available as a CSV, Shapefile, or other
structured format?

I will credit TPWD as the data source on the website.

Thank you for your help promoting public fishing access in Texas!

Best regards,
[Your Name]
```

## Testing the Pipeline 🧪

As you gather each dataset, test the ETL pipeline:

### Test Checklist

For each new dataset:

1. **Inspect the data:**
   ```bash
   python check_csv_columns.py path/to/new_data.csv
   ```

2. **Test with sample (first 10 rows):**
   ```python
   df = pd.read_csv('new_data.csv').head(10)
   df.to_csv('sample.csv')
   adapter.process_and_import('sample.csv')
   ```

3. **Verify in database:**
   ```sql
   SELECT * FROM fishing_spots
   WHERE data_source = 'New_Source_Name'
   LIMIT 10;
   ```

4. **Check frontend:**
   - Start Astro dev server
   - Search for new spots
   - Verify they display correctly

5. **Full import if successful:**
   ```python
   adapter.process_and_import('full_data.csv')
   ```

## Success Metrics 📊

**Phase 1 Complete When:**
- [ ] State Parks: 20+ parks imported
- [ ] Community Lakes: 30+ lakes imported
- [ ] ETL pipeline tested with 3+ different data formats
- [ ] Total spots: 2,500+ (current + new)
- [ ] All data properly tracked in data_sources table

**Phase 2 - Full Texas Coverage:**
- [ ] RACA: 200+ river access points
- [ ] Habitat Structures: Lake Fork + Sam Rayburn
- [ ] Total spots: 3,500+

**Phase 3 - Complete Texas:**
- [ ] All remaining sources
- [ ] Total spots: 4,000+
- [ ] Ready for second state

## Documentation 📚

**Reference Docs:**
- [DATA_ACQUISITION.md](data-pipeline/DATA_ACQUISITION.md) - Detailed plan for all sources
- [SCALING_GUIDE.md](data-pipeline/SCALING_GUIDE.md) - How to add new states
- [DATA_SOURCES.md](DATA_SOURCES.md) - Where to find data

## Questions/Blockers? 🤔

Common issues and solutions:

**"Can't find GPS coordinates for a spot"**
- Use Mapbox Geocoding API (free tier: 100,000 requests/month)
- Or Google Maps: right-click location → "What's here?"

**"CSV columns don't match expected format"**
- Use GenericCSVAdapter with custom column mapping
- See examples in SCALING_GUIDE.md

**"Data has duplicates"**
- ETL pipeline auto-generates unique slugs
- Check for true duplicates: same name + county + water body

**"Not sure if data is good quality"**
- Test with 10-row sample first
- Verify a few spots on Google Maps
- Check for null/zero coordinates

## Timeline Estimate ⏱️

**Realistic Goals:**
- **This Week:** State Parks + Community Lakes (~115 new spots)
- **Next Week:** RACA data (if TPWD responds) or Habitat Structures
- **Month 1:** 3,500+ total Texas spots
- **Month 2:** Complete Texas coverage, start second state

## When You're Ready for More States 🗺️

After Texas is complete and pipeline is proven:

**Best Next States:**
1. **Florida** - Similar data availability, huge fishing population
2. **Louisiana** - Adjacent state, good data
3. **California** - Large population, diverse fishing

**The adapter framework makes adding states easy:**
- Copy Texas adapter as template
- Map their CSV columns
- Import!

---

**Current Focus:** Data acquisition and pipeline testing

Everything is set up. Now it's just a matter of gathering the data and feeding it through the pipeline. Start with State Parks (quick win, unique content) then Community Lakes.

Good luck! 🎣
