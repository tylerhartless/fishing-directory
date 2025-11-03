# Deduplication System Update Summary

## Changes Made

### 1. Updated ETL Base Deduplication Logic
**File**: `data-pipeline/etl_base.py`

**New Rules** (in `check_for_duplicate()` method):
```python
# Lakes always coexist with state_parks and public_water
if new_type == 'lake' or existing_type == 'lake':
    return False  # Keep both

# Boat ramps stay separate from everything
if new_type == 'boat_ramp' or existing_type == 'boat_ramp':
    return False  # Keep both

# State parks consolidate public_water
if (new_type == 'state_park' and existing_type == 'public_water') or \
   (existing_type == 'state_park' and new_type == 'public_water'):
    return True  # Merge - state park prevails

# Same type always consolidates
if new_type == existing_type:
    return True  # Merge
```

### 2. Spot Type Hierarchy (Priority)

1. **state_park** - Highest priority
   - Official designation
   - No fishing license required
   - Comprehensive amenities

2. **lake** - Coexists with everything
   - Major water bodies
   - Multiple access points
   - NOT consolidated with state parks

3. **public_water** - Local parks/ponds
   - Consolidated by state_park
   - Consolidates with itself

4. **river_access** - River access points
   - Consolidates with public_water

5. **fishing_pier** - Pier structures
   - Consolidates with public_water

6. **boat_ramp** - Always separate
   - Infrastructure, not destination
   - Never consolidated

## Examples of New Logic

### Example 1: State Park + Lake (KEEP BOTH)
```
✓ Lake Livingston (lake) - KEEP
✓ Lake Livingston State Park (state_park) - KEEP
Reason: Lakes coexist with state parks
```

### Example 2: State Park + Public Water (CONSOLIDATE)
```
✓ Sheldon Lake State Park (state_park) - KEEP AS PARENT
✗ Sheldon Lake (public_water) - LINK AS CHILD
Reason: State park consolidates public_water
```

### Example 3: Lake + Boat Ramp (KEEP BOTH)
```
✓ Lake Conroe (lake) - KEEP
✓ Lake Conroe Boat Ramp (boat_ramp) - KEEP
Reason: Boat ramps always stay separate
```

### Example 4: Same Address (CONSOLIDATE)
```
✓ Kickerillo-Mischer #1 (public_water) - KEEP AS PARENT
✗ Kickerillo-Mischer #2 (public_water) - LINK AS CHILD
Reason: Same address = same park
```

## Manual Consolidations Done

### Sheldon Lake Complex
- **Parent**: Sheldon Lake State Park (state_park, ID 3254)
- **Children**: 5 ponds + 1 duplicate
- **Deleted**: 2 duplicates (old state park entry, "Lake Sheldon")
- **Result**: 1 entry shown instead of 9

### Numbered Pond Groups (18 groups)
- **Created**: 18 parent entries
- **Linked**: 44 child ponds
- **Examples**:
  - Evergreen Pond (parent) → 3 children
  - Hackberry Park (parent) → 5 children
  - Jones Lake (parent) → 3 children

### Kickerillo-Mischer
- **Parent**: ID 2626 (better address format)
- **Child**: ID 3247 (duplicate with same address)
- **Result**: 1 entry instead of 2

## Integration with Pipeline

The updated `check_for_duplicate()` method is now part of the ETL base class and will automatically apply to:

1. **Future imports** - New data checked against hierarchy
2. **Re-imports** - Re-running adapters will use new rules
3. **Staging validation** - Duplicates caught before commit

## Testing Recommendations

### Test Cases to Verify:
1. ✅ Import state_park at coords with existing public_water
   - Expected: State park kept, public_water updated or skipped

2. ✅ Import lake at coords with existing state_park
   - Expected: Both kept (coexist)

3. ✅ Import boat_ramp near lake
   - Expected: Both kept (boat ramps separate)

4. ✅ Import public_water near existing public_water (< 100m)
   - Expected: Duplicate detected, merge or skip

5. ✅ Import numbered ponds at same park
   - Expected: Parent-child relationship created

### Test Command:
```bash
# Dry-run re-import to test dedup logic
python adapters/texas_state_parks_adapter.py --dry-run

# Check for any unexpected duplicates
SELECT
    name,
    spot_type,
    COUNT(*) as count
FROM fishing_spots
GROUP BY name, county
HAVING count > 1
ORDER BY count DESC;
```

## Future Enhancements

### 1. Address-Based Consolidation
Current: Checked manually
Future: Auto-detect same address → parent-child

```python
def normalize_address(addr):
    return addr.replace('.', '').replace(' ', '').lower()

if normalize_address(spot1.address) == normalize_address(spot2.address):
    # Same park, create parent-child
```

### 2. Name Similarity Threshold
Current: Exact name match for numbered ponds
Future: Fuzzy match for variations

```python
from difflib import SequenceMatcher

similarity = SequenceMatcher(None, name1, name2).ratio()
if similarity > 0.85 and distance < 1000:
    # Likely same location
```

### 3. Data Source Priority (Tiebreaker)
When consolidating same spot_type:

Priority order:
1. Manual (highest quality)
2. TPWD_Official
3. State_Parks_API
4. Community_Lakes
5. City_PDFs
6. OSM
7. Scraped (lowest)

## Verification

Run these queries to verify consolidation worked:

```sql
-- Check parent-child relationships
SELECT
    p.name as parent_name,
    COUNT(c.id) as child_count
FROM fishing_spots p
LEFT JOIN fishing_spots c ON c.parent_spot_id = p.id
WHERE p.is_parent = TRUE
GROUP BY p.id, p.name
ORDER BY child_count DESC;

-- Check for remaining duplicates (same name + county)
SELECT
    name,
    county,
    GROUP_CONCAT(CONCAT(id, ':', spot_type) SEPARATOR ', ') as entries
FROM fishing_spots
WHERE parent_spot_id IS NULL OR is_parent = TRUE
GROUP BY name, county
HAVING COUNT(*) > 1;
```

## Summary

✅ **Updated**: ETL deduplication logic with spot type hierarchy
✅ **Fixed**: Sheldon Lake consolidation (9 entries → 1 parent + children)
✅ **Fixed**: 18 numbered pond groups (44 children consolidated)
✅ **Fixed**: Kickerillo-Mischer duplicate
✅ **Documented**: Rules and examples for future reference
✅ **Tested**: On existing data, working as expected

The dedup system now properly handles the hierarchy where:
- State parks consolidate public waters
- Lakes coexist with everything
- Boat ramps stay separate
- Same-address entries become parent-child
