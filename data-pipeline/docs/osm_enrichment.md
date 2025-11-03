# OpenStreetMap Enrichment

## Overview

The ETL pipeline now includes automatic OpenStreetMap (OSM) enrichment to improve data quality. When enabled, each fishing spot is cross-referenced with OSM to find:

1. **Water Body Names** - Actual lake/pond names instead of generic names
2. **Facility Information** - Park names, contact info, websites
3. **Amenities** - Parking, restrooms, boat ramps, picnic areas, fishing piers

## How It Works

### Integration Point

OSM enrichment runs automatically during the ETL `process_and_import()` method:

```
transform_row() → enrich_with_osm() → check_for_duplicate() → insert/update
```

### What Gets Enriched

**Water Body Names:**
- If OSM has a named water body within 200m of coordinates
- Overrides generic names like "Park Pond" with actual names like "Marshall Lake"
- Filters out island names to avoid confusion

**Amenities:**
- Queries OSM for features within 500m radius
- Finds: parking, toilets, picnic sites, boat ramps, fishing piers
- Merges with existing amenities (OSM data takes precedence)

**Facility Context:**
- Finds nearby parks, preserves, recreation areas
- Adds facility name and website to description when applicable

## Enabling OSM Enrichment

### Per-Adapter Configuration

```python
# Enable for specific adapter
adapter = TexasCommunityLakesAdapter(enable_osm_enrichment=True)

# Disable (default for most adapters)
adapter = TexasBoatRampsAdapter(enable_osm_enrichment=False)
```

### Recommended Usage

**Enable for:**
- Community fishing lakes (limited source data)
- User-submitted spots
- Generic "public water" spots

**Disable for:**
- State parks (already have detailed data)
- Boat ramps with comprehensive facility info
- High-volume imports (rate limiting makes it slow)

## Performance Considerations

### Rate Limiting
- OSM Overpass API allows ~2 requests/second
- Pipeline adds 0.6s delay between enrichment calls
- Enriching 100 spots takes ~60 seconds

### API Reliability
- Public OSM API can experience timeouts
- Enrichment fails gracefully (returns original data)
- Errors are logged but don't stop the pipeline

### Data Coverage
- Urban areas have excellent OSM coverage
- Rural fishing spots may have limited data
- Small ponds often lack names in OSM

## Example Output

### Before Enrichment
```json
{
  "name": "Albert Sallas County Park",
  "water_body_name": "Albert Sallas County Park",
  "amenities": {}
}
```

### After Enrichment
```json
{
  "name": "Albert Sallas County Park",
  "water_body_name": "Albert Sallas County Park",
  "amenities": {
    "parking": true,
    "restrooms": true,
    "picnic_area": true
  }
}
```

## OSM Query Details

### Search Radius
- **Water bodies**: 200m (must be very close to coordinates)
- **Facilities**: 300m (parks can be nearby)
- **Amenities**: 500m (parking lots can be at entrance)

### Queried Features
```
Water: natural=water, water=lake/pond/reservoir
Parks: leisure=park, leisure=nature_reserve
Amenities: amenity=parking/toilets/picnic_site
Boating: leisure=slipway/marina
```

## Testing

Run test with 3 spots:
```bash
cd data-pipeline/scripts
python test_osm_enrichment.py
```

Check enrichment on specific county:
```bash
python enrich_from_osm.py --county Montgomery --limit 10
```

## Future Improvements

1. **Batch Queries** - Query multiple spots in one Overpass request
2. **Caching** - Cache OSM results to avoid re-querying
3. **Name Matching** - Use fuzzy matching to identify official facility names
4. **Fallback APIs** - Use Nominatim when Overpass fails
5. **Manual Overrides** - Allow name_corrections.json to override OSM data

## Related Files

- [etl_base.py:155-219](../etl_base.py) - Base enrichment implementation
- [enrich_from_osm.py](../scripts/enrich_from_osm.py) - Standalone enrichment tool
- [texas_community_lakes_adapter.py](../adapters/texas_community_lakes_adapter.py) - Example usage
