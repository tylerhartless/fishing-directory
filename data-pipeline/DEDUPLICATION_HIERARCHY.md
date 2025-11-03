# Deduplication Hierarchy and Rules

## Spot Type Hierarchy (Priority Order)

When multiple entries exist for the same location, the following hierarchy determines which becomes the parent:

### 1. **State Park** (Highest Priority)
- **Why**: Official state designation, comprehensive amenities, established address
- **Example**: "Sheldon Lake State Park" prevails over "Sheldon Lake" or "Sheldon"
- **Characteristics**:
  - No fishing license required
  - Full facilities (restrooms, parking, picnic areas)
  - Official state address
  - Professional management

### 2. **Lake** (Large Public Waters)
- **Why**: Major water bodies that are destinations themselves
- **Example**: "Lake Conroe" prevails over "Conroe City Park"
- **Characteristics**:
  - Large surface area (typically 100+ acres)
  - Multiple access points
  - Regional significance
  - Often spans multiple counties

### 3. **Public Water** (Community/City Parks)
- **Why**: Managed public access with amenities
- **Example**: "Burke-Crenshaw Lake" prevails over "Burke-Crenshaw Pond #2"
- **Characteristics**:
  - City/county park with fishing access
  - Maintained facilities
  - Local significance

### 4. **River Access** (Natural Access Points)
- **Why**: Natural water body access
- **Example**: "Trinity River Access Point"
- **Characteristics**:
  - River/stream access
  - May be minimal facilities
  - Free public access

### 5. **Fishing Pier** (Specialized Access)
- **Why**: Dedicated fishing structure
- **Example**: "Galveston Fishing Pier"
- **Characteristics**:
  - Pier structure
  - Specific access point
  - May have fees

### 6. **Boat Ramp** (Lowest Priority - Usually Child)
- **Why**: Access infrastructure, not the destination
- **Example**: "Lake Houston Boat Ramp #3" is child of "Lake Houston"
- **Characteristics**:
  - Launch facility
  - Service infrastructure
  - Part of larger destination

## Deduplication Rules

### Rule 1: Same Name + Same Coordinates (< 100m apart)
```
If distance < 100m AND name similarity > 80%:
  → Merge into single entry
  → Use highest priority spot_type
```

**Example:**
- "Sheldon Lake State Park" (state_park) @ 29.8514, -95.1741
- "Sheldon Lake" (public_water) @ 29.8541, -95.1671
- **Result**: Keep state_park as parent, delete public_water

### Rule 2: Numbered Variants at Same Location (< 1000m)
```
If base_name matches AND distance < 1000m:
  → Create parent with base name
  → Link numbered entries as children
```

**Example:**
- "Evergreen Pond 1", "Evergreen Pond 2", "Evergreen Pond 3"
- **Result**: Create "Evergreen Pond" parent, hide numbered children

### Rule 3: Multiple Waters in Same Park (Same Address)
```
If same address OR distance < 500m AND different water_body_names:
  → Create park parent entry
  → Link individual ponds as children
```

**Example:**
- "Jesse H. Jones Park - Salad Bowl Pond"
- "Jesse H. Jones Park - Youth Fishing Lake"
- **Result**: "Jesse H. Jones Park and Nature Center" parent

### Rule 4: Boat Ramps at Lakes
```
If boat_ramp AND within 2km of lake/state_park:
  → Keep separate (different use case)
  → Don't parent to lake
```

**Example:**
- "Lake Houston" (lake)
- "Lake Houston Boat Ramp" (boat_ramp)
- **Result**: Keep both, don't merge (different user intent)

## Implementation Strategy

### Phase 1: Identify Duplicates
```sql
-- Find potential duplicates by name similarity and proximity
SELECT
    a.id as id1,
    a.name as name1,
    a.spot_type as type1,
    b.id as id2,
    b.name as name2,
    b.spot_type as type2,
    ST_Distance_Sphere(
        POINT(a.longitude, a.latitude),
        POINT(b.longitude, b.latitude)
    ) as distance_meters
FROM fishing_spots a
JOIN fishing_spots b ON a.id < b.id
WHERE
    SOUNDEX(a.name) = SOUNDEX(b.name)  -- Phonetic similarity
    AND ST_Distance_Sphere(
        POINT(a.longitude, a.latitude),
        POINT(b.longitude, b.latitude)
    ) < 1000
ORDER BY distance_meters;
```

### Phase 2: Apply Hierarchy
```python
def get_priority(spot_type):
    hierarchy = {
        'state_park': 1,
        'lake': 2,
        'public_water': 3,
        'river_access': 4,
        'fishing_pier': 5,
        'boat_ramp': 6
    }
    return hierarchy.get(spot_type, 99)

def resolve_duplicate(spot1, spot2):
    priority1 = get_priority(spot1['spot_type'])
    priority2 = get_priority(spot2['spot_type'])

    if priority1 < priority2:
        return spot1  # spot1 is parent
    elif priority2 < priority1:
        return spot2  # spot2 is parent
    else:
        # Same priority - use data source quality
        return resolve_by_source(spot1, spot2)
```

### Phase 3: Data Source Priority (Tiebreaker)
When spot_type is the same:
1. **Manual** (highest quality)
2. **TPWD_Official** (state agency data)
3. **State_Parks_API** (official park data)
4. **Community_Lakes** (curated list)
5. **City_PDFs** (city data)
6. **OSM** (crowdsourced)
7. **Scraped** (lowest - needs validation)

## Automation Script Location

**File**: `data-pipeline/dedupe.py`

### Usage:
```bash
# Dry-run to preview changes
python dedupe.py --dry-run

# Apply deduplication
python dedupe.py --apply

# Apply to specific county
python dedupe.py --county=Harris --apply
```

### Output:
```
=== DEDUPLICATION REPORT ===
Found 47 duplicate groups

Group 1: Sheldon Lake (3 entries)
  [PARENT] ID 800: Sheldon Lake State Park (state_park)
  [DELETE] ID 2648: Sheldon (public_water) - 250m away
  [DELETE] ID 3171: Lake Sheldon (lake) - 300m away
  Action: Set 800 as parent, delete 2648 and 3171

Group 2: Bastrop State Park (2 entries)
  [PARENT] ID 2270: Bastrop State Park (state_park)
  [CHILD]  ID 2271: Bastrop State Park Lake #2 (public_water)
  Action: Link 2271 as child of 2270
```

## Manual Review Required

Some cases need human judgment:

### Case 1: Different Facilities with Same Name
```
- "Martin Lake" (private, Rusk County)
- "Martin Lake" (public, Panola County)
→ Keep both (different locations, >50km apart)
```

### Case 2: Historical vs Current Names
```
- "Old Coleman Lake" (historical)
- "Coleman City Lake" (current)
→ Keep current, add note to historical
```

### Case 3: Seasonal vs Permanent
```
- "Choke Canyon State Park - South Shore"
- "Choke Canyon State Park - Calliham Unit"
→ Keep both (different units, >20km apart)
```

## Testing Strategy

### Test Cases:
1. ✅ State park + public water at same coords → Keep state park
2. ✅ Numbered ponds within 1000m → Create parent
3. ✅ Boat ramp near lake → Keep separate
4. ✅ Different lakes 50km+ apart → Keep both
5. ✅ Same address different water bodies → Parent-child

### Validation:
- Run against current 4,200 spots
- Expect 50-100 deduplication actions
- Manual review of all deletions
- Backup database before applying

## Integration with Pipeline

### ETL Flow:
```
1. Import raw data → staging table
2. Geocode addresses
3. OSM enrichment
4. **→ DEDUPLICATION (this step)**
5. Validation
6. Commit to production DB
```

This ensures new data is deduplicated before going live.
