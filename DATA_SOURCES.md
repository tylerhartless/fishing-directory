# Data Sources Guide

This document lists all the data sources you can use to populate your fishing directory, starting with Texas.

## 🎣 Texas Data Sources (Start Here)

### 1. TPWD Boat Ramps ⭐ **START WITH THIS**

**What:** Official boat ramp locations across Texas
**Estimated Records:** 2,000-3,000 spots
**Data Quality:** Excellent - verified by state

**How to Get:**
1. Visit: https://tpwd.texas.gov/gis/resources/boat-access.phtml
2. Look for downloadable data (CSV, Shapefile, or GeoJSON)
3. Alternative: https://tpwd.texas.gov/fishboat/fish/recreational/lakes/
4. If direct download isn't available, contact TPWD GIS department: gisdata@tpwd.texas.gov

**Expected Fields:**
- Ramp name
- County
- Water body
- Latitude/Longitude
- Amenities (parking, restrooms, etc.)

**Script to Use:** `process_boat_ramps.py`

---

### 2. Texas State Parks with Fishing

**What:** State parks offer FREE fishing (no license required!)
**Estimated Records:** 50-100 parks
**Data Quality:** Excellent

**How to Get:**
1. Visit: https://tpwd.texas.gov/state-parks/parks/find-a-park
2. Filter for parks with fishing
3. Manual entry OR scrape park details
4. I've included 3 examples in `process_state_parks.py` - expand this list

**Parks to Add:**
- Brazos Bend State Park
- Inks Lake State Park
- Lake Brownwood State Park
- Caddo Lake State Park
- Enchanted Rock (limited fishing)
- And ~50 more...

**Script to Use:** `process_state_parks.py` (expand the array)

---

### 3. Community Fishing Lakes (CFL)

**What:** TPWD-managed lakes stocked with fish, often with easy bank access
**Estimated Records:** 40+ lakes
**Data Quality:** Excellent

**How to Get:**
1. Visit: https://tpwd.texas.gov/fishboat/fish/recreational/lakes/
2. Look for "Community Fishing Lakes" section
3. Each lake page has coordinates and amenities

**Example Lakes:**
- Lake Pflugerville (Austin area)
- Tom Bass Park (Houston)
- Chisholm Park Pond (Killeen)
- Many more across Texas

**Script to Create:** `process_cfl.py` (similar to state parks)

---

### 4. River Access (RACA) Points

**What:** Public river access leases on private land
**Estimated Records:** 200+ access points
**Data Quality:** Good

**How to Get:**
1. Visit: https://tpwd.texas.gov/fishboat/fish/recreational/raca/
2. Click on each river system
3. Download PDF maps or contact TPWD for coordinates

**Rivers with RACA:**
- Guadalupe River
- Llano River
- San Marcos River
- Colorado River
- Many more

**Note:** May require some manual geocoding if only addresses provided

---

### 5. Fish Habitat Structures

**What:** Underwater fish attractors (tire reefs, brush piles, etc.)
**Estimated Records:** 1,000+ structures
**Data Quality:** Good (coordinates may vary in precision)

**How to Get:**
1. Visit: https://tpwd.texas.gov/fishboat/fish/habitats/
2. Select specific lakes (Lake Fork, Lake Sam Rayburn, etc.)
3. Download coordinates for fish attractors

**Popular Lakes with Structure Data:**
- Lake Fork
- Lake Sam Rayburn
- Toledo Bend
- Lake Texoma

**Script to Create:** `process_habitat_structures.py`

---

### 6. Public Fishing Piers

**What:** Fixed fishing piers, often lighted and handicap accessible
**Estimated Records:** 100+ piers
**Data Quality:** Good

**How to Get:**
1. Included in boat ramp data sometimes
2. Search TPWD website for "fishing pier"
3. Coastal piers: https://tpwd.texas.gov/fishboat/fish/recreational/coastal/

**Types:**
- Lighted fishing piers
- Galveston fishing pier
- Corpus Christi area piers
- Lake piers

---

## 🌊 Coastal Fishing Access (Texas)

### 7. Wade Fishing Access Points

**What:** Beach and bay access for wade fishing
**Estimated Records:** 100+ spots
**Data Quality:** Good

**How to Get:**
1. Visit: https://tpwd.texas.gov/fishboat/fish/recreational/coastal/
2. Look for "Wade Fishing" sections
3. Padre Island National Seashore access points
4. Galveston Bay area

---

## 📊 How Much Data Can You Get?

**Conservative Estimate (Texas Only):**
- Boat Ramps: 2,500
- State Parks: 75
- Community Fishing Lakes: 40
- RACA River Access: 200
- Fish Habitat Structures: 1,000
- Fishing Piers: 100
- Coastal Access: 100

**TOTAL: ~4,000 fishing spots for Texas**

With detailed write-ups and unique pages, that's **4,000 SEO-optimized pages** just from free government data!

---

## 🚀 Recommended Data Collection Order

### Week 1: Core Data
1. ✅ **TPWD Boat Ramps** - This is your foundation
2. ✅ **Texas State Parks** - High-quality content, unique angle (free fishing)
3. ✅ **Community Fishing Lakes** - Good for urban areas

### Week 2: Expansion
4. **RACA River Access** - Adds river fishing
5. **Major Lake Fish Structures** - Start with popular lakes (Fork, Sam Rayburn)

### Week 3: Coastal & Specialty
6. **Coastal Access Points** - If targeting Gulf coast
7. **Public Fishing Piers** - Unique content angle

---

## 🔧 Data Collection Tools

### Option 1: Direct Download (Easiest)
- Contact TPWD GIS department: gisdata@tpwd.texas.gov
- Request: "Boat ramp shapefile or CSV for public access"
- They're usually very helpful for public data requests

### Option 2: Manual Collection
- Use Google Sheets to organize
- Columns: Name, County, Water Body, Lat, Lon, Amenities
- Then export to CSV and run through your scripts

### Option 3: Web Scraping (Advanced)
- Use Python Beautiful Soup or Scrapy
- Scrape TPWD website systematically
- **Note:** Check their robots.txt and be respectful

---

## 🗺️ Getting Coordinates

If you have addresses but no coordinates:

### Use Mapbox Geocoding (Free Tier)
```python
import requests

def geocode_address(address):
    token = 'your_mapbox_token'
    url = f'https://api.mapbox.com/geocoding/v5/mapbox.places/{address}.json'
    params = {'access_token': token, 'limit': 1}

    response = requests.get(url, params=params)
    data = response.json()

    if data['features']:
        coords = data['features'][0]['center']
        return coords[1], coords[0]  # lat, lon
    return None, None
```

### Or Use Google Sheets
- Google Sheets has a built-in geocoding feature
- Add-on: "Geocode by Awesome Table"

---

## 📧 Contacting TPWD for Data

**Email Template:**

```
Subject: Public Data Request - Boat Ramp Locations

Hello,

I'm building a public fishing access directory to help Texas anglers
find fishing spots more easily. I'm looking for geographic data on:

- Public boat ramp locations
- Coordinates (latitude/longitude)
- Amenity information (parking, restrooms, etc.)

Is this data available as a CSV, Shapefile, or GeoJSON download?

I plan to credit TPWD as the data source on my website.

Thank you for your help promoting public fishing access in Texas!

Best regards,
[Your Name]
```

---

## 🌍 Future State Expansion

Once you have Texas dialed in, here are the best states to add next:

### Tier 1: High Fishing Population
1. **Florida** - FWC has excellent GIS data
2. **Louisiana** - LDWF boat ramp data
3. **Michigan** - Great Lakes + inland lakes
4. **Minnesota** - "Land of 10,000 Lakes"

### Tier 2: Good Data Availability
5. **California** - CDFW data
6. **Wisconsin** - DNR has great datasets
7. **North Carolina** - Coastal + inland
8. **Alabama** - Good coastal fishing

### Data Sources for Other States:
- Most states have a "Wildlife GIS Data" page
- Search: "[State] fish wildlife GIS data download"
- Example: "Florida FWC GIS data"

---

## 💡 Pro Tips

1. **Start Small:** Get 100 perfect boat ramps imported before aiming for 1,000
2. **Quality > Quantity:** Better to have great descriptions for 500 spots than bare data for 5,000
3. **Document Sources:** Always note where data came from in the `data_source` field
4. **Verify Coordinates:** Spot-check coordinates on Google Maps before importing thousands
5. **Update Regularly:** Government data changes - plan to refresh annually

---

## 🎯 Your First Data Collection Task

**Right Now - Do This:**

1. Visit https://tpwd.texas.gov/gis/resources/boat-access.phtml
2. Look for a download link (CSV, Shapefile, or GeoJSON)
3. If you find it, download and save to `raw-data/tpwd_boat_ramps.csv`
4. If not, send the email template above to gisdata@tpwd.texas.gov

**Then:**
5. Set up your Python environment
6. Configure `.env` with your Hostinger database credentials
7. Run `python process_boat_ramps.py`
8. Watch 2,500+ spots get imported in seconds!

---

Need help with any specific data source? Let me know!
