# Texas Community Fishing Lakes - Data Acquisition

## Overview
TPWD maintains a web map of 785+ community fishing lakes at:
https://tpwd.texas.gov/fishboat/fish/recreational/lakes/cfl.phtml

## Scraping Approach

### 1. Data Location
The website uses **Leaflet.js** with ESRI basemaps to display lake locations. The data is stored in a separate JavaScript file:
```
https://tpwd.texas.gov/fishboat/fish/recreational/lakes/media/cfl.js
```

### 2. Data Format
The `cfl.js` file contains a GeoJSON FeatureCollection in a JavaScript variable:

```javascript
var cfls = {
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "properties": {
        "ID": "0088",
        "name": "Blue",
        "county": "Anderson",
        "size": "5.00"
      },
      "geometry": {
        "type": "Point",
        "coordinates": [-95.6552, 31.763]
      }
    },
    // ... more features
  ]
};
```

### 3. Data Fields
Each lake entry contains:
- **ID**: Unique identifier (e.g., "0088")
- **name**: Lake name (e.g., "Blue")
- **county**: Texas county (e.g., "Anderson")
- **size**: Surface area in acres (e.g., "5.00")
- **coordinates**: [longitude, latitude] in EPSG:4326 (WGS84)

### 4. Extraction Steps

#### Step 1: Download the JavaScript file
```bash
curl -o raw-data/cfl.js https://tpwd.texas.gov/fishboat/fish/recreational/lakes/media/cfl.js
```

#### Step 2: Convert to clean JSON
```bash
cd data-pipeline/scripts
python convert_cfl_to_json.py
```

This script:
- Extracts the GeoJSON from the JavaScript variable
- Removes trailing commas (JavaScript allows them, JSON doesn't)
- Saves as `raw-data/community_fishing_lakes.json`

#### Step 3: Import via ETL adapter
```bash
cd data-pipeline/adapters
python texas_community_lakes_adapter.py
```

This adapter:
- Loads the GeoJSON
- Transforms each feature into `FishingSpotData`
- Validates coordinates (skips invalid [0,0] entries)
- Sets `spot_type='community_lake'`
- Applies deduplication (100m radius, same spot_type only)

## Data Quality Notes

1. **Invalid Coordinates**: Some entries have `[0,0]` coordinates and are skipped
2. **Coordinate System**: Data is already in WGS84 (EPSG:4326), no conversion needed
3. **Deduplication**: Won't merge with state parks or boat ramps at same location (different spot_types)

## Update Frequency

The TPWD map is updated periodically as new lakes are added to the program. To refresh:
1. Re-download `cfl.js`
2. Re-run the conversion script
3. Re-import via the adapter

## Alternative Approach (Browser-based)

If the JavaScript file structure changes, you can extract data from the browser console:

```javascript
// Open https://tpwd.texas.gov/fishboat/fish/recreational/lakes/cfl.phtml
// In browser console:
console.log(JSON.stringify(cfls, null, 2));
// Copy the output and save as JSON
```

## Future Enhancements

- Add geocoding to get city names
- Scrape individual lake pages for more details (if available)
- Add fishing reports if TPWD provides them
- Track stocking schedules
