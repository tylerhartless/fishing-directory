# Generic GeoJSON Scraper for Leaflet/ESRI Maps

## Overview

The `scrape_leaflet_geojson.py` script is a **generic, reusable tool** for extracting GeoJSON data from any website that uses Leaflet.js or ESRI mapping libraries to display geographic data.

## Why This Exists

Many government agencies and organizations use similar mapping stacks (Leaflet + ESRI) to display data. Instead of writing custom scrapers for each site, this tool automatically detects and extracts GeoJSON data using multiple strategies.

## Supported Data Loading Patterns

The scraper automatically handles multiple ways that GeoJSON might be loaded:

### 1. **Inline JavaScript Variable**
```javascript
var myData = {"type": "FeatureCollection", "features": [...]};
```

### 2. **External .js File**
```html
<script src="/data/locations.js"></script>
```
Where `locations.js` contains:
```javascript
var locations = {"type": "FeatureCollection", ...};
```

### 3. **External .json or .geojson File**
```html
<script>
  fetch('/data/points.json')
    .then(response => response.json())
    ...
</script>
```

### 4. **API Endpoints**
- `/api/data`
- `map.php?get=json`
- ArcGIS REST services

## Usage

### Basic Usage
```bash
cd data-pipeline/scripts
python scrape_leaflet_geojson.py <URL>
```

### With Custom Output Filename
```bash
python scrape_leaflet_geojson.py <URL> --output filename.json
```

## Examples

### Texas Community Fishing Lakes
```bash
python scrape_leaflet_geojson.py \
  https://tpwd.texas.gov/fishboat/fish/recreational/lakes/cfl.phtml \
  --output ../../raw-data/tx_community_lakes.json
```

**Result**: 785 community fishing lakes with properties: `ID`, `name`, `county`, `size`

### California State Parks (hypothetical)
```bash
python scrape_leaflet_geojson.py \
  https://parks.ca.gov/fishing-map \
  --output ../../raw-data/ca_fishing_spots.json
```

### Florida Wildlife Areas (hypothetical)
```bash
python scrape_leaflet_geojson.py \
  https://myfwc.com/interactive-maps/wildlife-areas \
  --output ../../raw-data/fl_wildlife_areas.json
```

## How It Works

### Step 1: Page Analysis
The scraper fetches the HTML and analyzes it for potential GeoJSON sources:
- Scans `<script src="...">` tags for `.js` files
- Examines inline `<script>` blocks for variable declarations
- Looks for `.json` and `.geojson` file references
- Detects API endpoint patterns

### Step 2: Smart Extraction
For each potential source, the scraper:
1. Fetches the content (if external URL)
2. Uses regex to find GeoJSON structures
3. Extracts complete objects using balanced brace matching
4. Cleans JavaScript-specific syntax:
   - Removes trailing commas
   - Decodes HTML entities (`&amp;#39;` → `'`)
   - Strips comments

### Step 3: Validation
- Checks if data is valid GeoJSON
- Verifies `type` field (`FeatureCollection`, `Feature`, etc.)
- Ensures `features` array exists for FeatureCollections

### Step 4: Save
- Saves to clean, formatted JSON
- Reports feature count and sample properties

## What Gets Extracted

The scraper preserves the complete GeoJSON structure:

```json
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "properties": {
        "name": "Lake Name",
        "county": "County Name",
        "size": "10.5",
        ...
      },
      "geometry": {
        "type": "Point",
        "coordinates": [-95.123, 30.456]
      }
    }
  ]
}
```

## Limitations

### What It Can Handle
✓ Static GeoJSON data loaded on page load
✓ External `.js` files with variable declarations
✓ Direct `.json`/`.geojson` files
✓ Simple API endpoints

### What It Cannot Handle
✗ Data loaded dynamically via complex AJAX after page load
✗ Data behind authentication
✗ Data requiring POST requests with specific parameters
✗ WebSocket-based data streaming
✗ Data embedded in React/Vue components

## Troubleshooting

If the scraper fails to find GeoJSON:

### 1. **Check Browser DevTools**
Open the target page in your browser:
1. Open DevTools (F12)
2. Go to Network tab
3. Reload the page
4. Look for `.js`, `.json`, or API calls
5. Find the actual data source URL

### 2. **Manual Extraction from Browser Console**
If data is loaded dynamically:
```javascript
// In browser console on the target page:
// Find the variable name (inspect the map code)
console.log(JSON.stringify(yourVariableName, null, 2));
// Copy output and save as JSON
```

### 3. **Inspect Page Source**
Look for:
- Variable declarations: `var data = `
- Script sources: `<script src=`
- Fetch/AJAX calls: `fetch(`, `$.ajax(`

## Integration with ETL Pipeline

Once you've scraped GeoJSON data:

### 1. Create an Adapter
```python
# data-pipeline/adapters/new_state_adapter.py
from etl_base import BaseDataAdapter, FishingSpotData

class NewStateAdapter(BaseDataAdapter):
    def load_data(self, file_path: str):
        with open(file_path) as f:
            geojson = json.load(f)
        # Convert to DataFrame
        ...

    def transform_row(self, row, index):
        # Transform to FishingSpotData
        ...
```

### 2. Import Data
```bash
cd data-pipeline/adapters
python new_state_adapter.py
```

## Advanced Usage

### Scraping Multiple Sites
Create a batch script:
```bash
#!/bin/bash
# scrape_all_states.sh

python scrape_leaflet_geojson.py https://tpwd.texas.gov/map --output tx.json
python scrape_leaflet_geojson.py https://parks.ca.gov/map --output ca.json
python scrape_leaflet_geojson.py https://myfwc.com/map --output fl.json
```

### Automating Updates
```bash
# cron job to refresh data weekly
0 0 * * 0 /path/to/scrape_all_states.sh
```

## Future Enhancements

Potential improvements:
- [ ] Add support for Selenium/Playwright for JavaScript-heavy sites
- [ ] Handle paginated API responses
- [ ] Support authentication (API keys, OAuth)
- [ ] Add caching to avoid re-downloading unchanged data
- [ ] Support for other geometry types (Polygon, LineString)
- [ ] Automatic conversion of non-WGS84 coordinate systems

## Related Files

- **Scraper**: `data-pipeline/scripts/scrape_leaflet_geojson.py`
- **Community Lakes Adapter**: `data-pipeline/adapters/texas_community_lakes_adapter.py`
- **ETL Base**: `data-pipeline/etl_base.py`

## When to Use This vs. Manual Download

**Use the scraper when:**
- Data is embedded in a webpage
- No official download link exists
- Data updates frequently
- You need to automate collection

**Download manually when:**
- Official data export/download exists
- Data is in better format (CSV, Shapefile)
- Data rarely changes
- API documentation exists
