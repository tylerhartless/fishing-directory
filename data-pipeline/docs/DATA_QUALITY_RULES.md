# Data Quality Rules & Standards

## Overview

This document defines the rules for cleaning, validating, and standardizing fishing spot data. These rules should be applied consistently across all sources and enforced during the staging/validation phase.

## Naming Rules

### Rule 1: Separate Park Names from Water Body Names

**Problem:** Many sources combine park and water body into one name
- Bad: "Alexander Deussen Park on Lake Houston"
- Bad: "Toledo Bend Reservoir - Sabine County Access"

**Solution:**
```
name: "Alexander Deussen Park"
water_body_name: "Lake Houston"

name: "Sabine County Park"  (or actual park name if known)
water_body_name: "Toledo Bend Reservoir"
```

**Detection Pattern:**
```python
# Patterns to detect combined names
patterns = [
    r"(.+?) on (.+)",           # "Park on Lake"
    r"(.+?) at (.+)",           # "Park at Lake"
    r"(.+?) - (.+) Access",     # "Lake - County Access"
    r"(.+?) \((.+?)\)",         # "Park (Lake)"
]
```

**Extraction Logic:**
1. If pattern matches, extract both parts
2. Determine which is park vs water body:
   - Contains "Park", "Access", "Recreation Area" → likely facility name
   - Contains "Lake", "Pond", "Reservoir", "River", "Creek" → likely water body
3. If unsure, check OSM data for confirmation

### Rule 2: Unknown Water Bodies

**Problem:** Sometimes we don't know the actual water body name

**Solution:** Use standardized placeholders based on context

```python
# If we have a park/facility name but unknown water body
water_body_name = f"{facility_name} Waters"
# Example: "Memorial Park Waters"

# If we have neither
water_body_name = "Park Waters"  # Generic fallback

# NEVER use:
water_body_name = None
water_body_name = name  # Don't duplicate the name field
```

**Priority for Water Body Names:**
1. OSM data (if within 200m)
2. TPWD source data (Community Lakes, etc.)
3. City PDF data (if explicitly listed)
4. "{facility_name} Waters"
5. "Park Waters" (last resort)

### Rule 3: Remove Redundant Prefixes/Suffixes

**Problem:** Sources add redundant location info
- Bad: "Lake Conroe - Montgomery County - Texas"
- Bad: "Benbrook Lake (Fort Worth)"

**Solution:**
```python
# Remove these patterns
redundant_patterns = [
    r"\s*-\s*Texas$",
    r"\s*,\s*TX$",
    r"\s*\([^)]*County[^)]*\)",  # (County info)
    r"\s*-\s*[A-Z][a-z]+\s+County",  # - County Name
]

# Clean:
"Lake Conroe - Montgomery County - Texas" → "Lake Conroe"
"Benbrook Lake (Fort Worth)" → "Benbrook Lake"
```

### Rule 4: Standardize Spot Type Names

**Problem:** Inconsistent facility type naming

**Bad Examples:**
- "Lake Como Park"
- "River Park Access Point"
- "Houston City Lake #3"

**Good Examples:**
```
name: "Lake Como Park"
water_body_name: "Lake Como"
spot_type: "public_water"

name: "River Park"
water_body_name: "Trinity River"
spot_type: "river_access"

name: "City Park"
water_body_name: "City Park Pond #3"
spot_type: "public_water"
```

## Data Validation Rules

### Coordinates

```python
def validate_coordinates(lat, lon, county):
    # Must be in Texas
    if not (25.8 <= lat <= 36.5 and -106.7 <= lon <= -93.5):
        return False, "Coordinates outside Texas"

    # Must match stated county (reverse geocode check)
    actual_county = reverse_geocode(lat, lon)
    if actual_county != county:
        return False, f"Coordinates in {actual_county}, not {county}"

    return True, None
```

### Duplicates

```python
def check_duplicate(spot, existing_spots):
    # Exact name + county match
    for existing in existing_spots:
        if (spot['name'] == existing['name'] and
            spot['county'] == existing['county']):
            return True, "exact_match"

    # Nearby coordinates (within 100m)
    for existing in existing_spots:
        distance = haversine(spot['lat'], spot['lon'],
                           existing['lat'], existing['lon'])
        if distance < 100:
            return True, "nearby_coordinates"

    return False, None
```

### Required Fields

```python
REQUIRED_FIELDS = {
    'name': str,           # Must not be empty
    'latitude': float,     # Must be valid coordinate
    'longitude': float,    # Must be valid coordinate
    'county': str,         # Must be valid Texas county
    'spot_type': str,      # Must be in enum
    'state': str,          # Must be 'TX'
}

OPTIONAL_BUT_IMPORTANT = {
    'water_body_name': str,  # Should follow naming rules
    'address': str,          # Prefer over just coords
    'amenities': dict,       # Merge from all sources
    'description': str,      # Generated if missing
}
```

## Description Generation Rules

Descriptions should be short, factual, and consistent:

```python
def generate_description(spot_type, data_source, amenities):
    templates = {
        'state_park': "State park with fishing access. No fishing license required.",
        'community_lake': "Community fishing lake regularly stocked by TPWD.",
        'neighborhood_fishing': "Neighborhood fishing spot regularly stocked by TPWD.",
        'lake': "Large reservoir with diverse fishing opportunities.",
        'boat_ramp': "Public boat ramp with water access.",
        'public_water': "Public water access for fishing.",
        'river_access': "River access point for fishing.",
        'fishing_pier': "Public fishing pier.",
    }

    return templates.get(spot_type, "Public fishing access.")
```

**Never include in descriptions:**
- Target species (will be separate field)
- Specific amenity details (in amenities field)
- Park/lake names (already in name/water_body fields)
- Stocking schedules (too specific, changes)

## Source Priority & Conflict Resolution

### When Multiple Sources Have Same Spot

```python
def resolve_conflicts(sources):
    result = {}

    # Coordinates - use highest confidence
    coord_priority = ['GPS', 'City_PDF', 'OSM', 'Geocoded']
    result['coords'] = pick_by_priority(sources, 'coords', coord_priority)

    # Facility name - City PDFs usually better
    name_priority = ['City_PDF', 'Community_Lake', 'State_Park', 'Lake_Scrape']
    result['name'] = pick_by_priority(sources, 'name', name_priority)

    # Water body - OSM usually most accurate
    water_priority = ['OSM', 'Community_Lake', 'City_PDF', 'Lake_Scrape']
    result['water_body'] = pick_by_priority(sources, 'water_body', water_priority)

    # Address - City PDFs best, then OSM
    addr_priority = ['City_PDF', 'OSM', 'Geocoded']
    result['address'] = pick_by_priority(sources, 'address', addr_priority)

    # Amenities - merge all (union)
    result['amenities'] = merge_amenities(sources)

    # Stocking info - ONLY from TPWD sources
    if any(s['source'].startswith('TPWD') for s in sources):
        tpwd = [s for s in sources if s['source'].startswith('TPWD')][0]
        result['stocking'] = tpwd.get('stocking')

    return result
```

## Sanity Check Process

### Phase 1: Export Current Data
```bash
# Export all current Texas spots to JSON
python scripts/export_current_data.py --state TX --output staged/current/texas_current.json
```

### Phase 2: Run Through New Pipeline
```bash
# Process all sources through new pipeline
python pipeline/process_all_sources.py --state TX --validate-only

# Output: staged/validated/texas_new.json
```

### Phase 3: Compare
```bash
# Generate comparison report
python pipeline/compare_datasets.py \
  --current staged/current/texas_current.json \
  --new staged/validated/texas_new.json \
  --output staged/reports/texas_comparison.json
```

**Comparison Report Should Show:**
```json
{
  "summary": {
    "current_count": 4235,
    "new_count": 4180,
    "spots_removed": 58,     // Duplicates detected
    "spots_added": 3,        // New spots found
    "spots_changed": 347     // Data improved
  },
  "removed_spots": [
    {
      "id": 3234,
      "name": "American Legion Park Pond",
      "reason": "Duplicate of ID 3280",
      "county": "Harris"
    }
  ],
  "changed_spots": [
    {
      "id": 2804,
      "field": "name",
      "old": "Albert Sallas County Park",
      "new": "A.V. 'Bull' Sallas Park",
      "reason": "Better name from City PDF source"
    },
    {
      "id": 3233,
      "field": "water_body_name",
      "old": "Alexander Deussen Park on Lake Houston",
      "new": "Lake Houston",
      "reason": "Separated park from water body"
    }
  ],
  "validation_errors": [
    {
      "source": "DFW PDF",
      "spot": "Bachman Lake",
      "error": "Coordinates outside stated county"
    }
  ]
}
```

### Phase 4: Manual Review
```bash
# Generate human-readable report
python pipeline/generate_review_report.py \
  --comparison staged/reports/texas_comparison.json \
  --output staged/reports/texas_review.md
```

**Review Report Format:**
```markdown
# Texas Data Sanity Check Report

## Summary
- Current: 4,235 spots
- New: 4,180 spots
- Removed: 58 duplicates
- Changed: 347 improvements
- Errors: 12 validation failures

## Duplicates Removed (58)

### American Legion Park Pond
- **Removed ID:** 3234 (Harris County)
- **Kept ID:** 3280 (Fort Bend County)
- **Reason:** Same coordinates (29.5918, -95.5128)
- **Action:** ✅ Correct - Missouri City is in Fort Bend

### Toledo Bend Access - Sabine #007
- **Removed ID:** 1676
- **Kept ID:** 1677
- **Reason:** Within 50m, same name
- **Action:** ⚠️ REVIEW - May be separate boat ramps

## Name Changes (347)

### A.V. 'Bull' Sallas Park
- **Old:** Albert Sallas County Park
- **New:** A.V. 'Bull' Sallas Park
- **Source:** City PDF had better name
- **Action:** ✅ Correct

### Lakeside Park
- **Old:** Andrews City
- **New:** Lakeside Park
- **Water Body:** Andrews City Lake
- **Action:** ✅ Correct - separated park from lake

## Validation Errors (12)

### Bright Lake at Old Settlers Park
- **Error:** No coordinates
- **Source:** Austin PDF
- **Action:** ⚠️ Need manual geocoding

## Added Spots (3)

### New Spot: Lake Pflugerville Dock
- **Source:** OSM
- **Coords:** 30.4393, -97.6201
- **Action:** ⚠️ REVIEW - Verify it's actually public fishing
```

## Implementation Checklist

- [ ] Create naming rule validator
- [ ] Create water body fallback logic
- [ ] Implement source priority resolution
- [ ] Build duplicate detection
- [ ] Create description generator
- [ ] Export current data to JSON
- [ ] Process all sources through pipeline
- [ ] Generate comparison report
- [ ] Manual review of differences
- [ ] Document all changes
- [ ] Re-import when satisfied

## Example: Full Validation Flow

```python
# validation_pipeline.py

def validate_spot(raw_spot, existing_spots):
    """Full validation of a single spot"""

    # 1. Clean and separate names
    cleaned = clean_combined_names(raw_spot)

    # 2. Validate water body name
    if not cleaned['water_body_name']:
        cleaned['water_body_name'] = generate_water_body_fallback(
            cleaned['name']
        )

    # 3. Validate coordinates
    valid, error = validate_coordinates(
        cleaned['latitude'],
        cleaned['longitude'],
        cleaned['county']
    )
    if not valid:
        return None, error

    # 4. Check for duplicates
    is_dup, dup_type = check_duplicate(cleaned, existing_spots)
    if is_dup:
        return None, f"Duplicate ({dup_type})"

    # 5. Generate description if missing
    if not cleaned['description']:
        cleaned['description'] = generate_description(
            cleaned['spot_type'],
            cleaned['data_source'],
            cleaned['amenities']
        )

    # 6. Remove redundant info
    cleaned['name'] = remove_redundant_patterns(cleaned['name'])

    return cleaned, None
```

## Success Criteria

Before committing reimported Texas data:

1. ✅ All duplicates resolved (manual review required)
2. ✅ All name/water_body separations correct
3. ✅ No "null" or missing water_body_names (use fallbacks)
4. ✅ All descriptions standardized and short
5. ✅ Coordinates validated against counties
6. ✅ Source priority rules applied consistently
7. ✅ Comparison report reviewed and approved
8. ✅ Spot count makes sense (current ± expected changes)
