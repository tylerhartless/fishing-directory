# Park Consolidation Strategy

## Problem Statement

Some parks/nature centers have multiple fishing ponds or water bodies, but they all share the same address (access point). Currently, these show up as separate listings, which creates:
- Duplicate search results
- Confusing user experience (seeing the same park name 3 times)
- Data quality issues (which one is the "main" entry?)

## Solution: Display Consolidation with Data Preservation

**Core Principle**: Same address = Same listing (for display purposes)

### Data Model

We keep the individual water bodies in the database (for species tracking, stocking data, etc.) but consolidate them for display.

#### Option 1: Parent-Child Relationship (Recommended)

**Database Changes:**
```sql
ALTER TABLE fishing_spots ADD COLUMN parent_spot_id INT NULL;
ALTER TABLE fishing_spots ADD COLUMN is_parent BOOLEAN DEFAULT FALSE;
ALTER TABLE fishing_spots ADD INDEX idx_parent (parent_spot_id);
```

**Example Structure:**
```
Jesse H. Jones Park and Nature Center (ID 3290)
├─ is_parent: TRUE
├─ water_body_name: "Spring Creek" (primary water body)
├─ child_spots: [2641, 2647]
│
├── Salad Bowl Pond (ID 2647)
│   ├─ parent_spot_id: 3290
│   ├─ is_parent: FALSE
│   └─ Show as sub-listing or hide from main search
│
└── Jones Youth Fishing Lake (ID 2641)
    ├─ parent_spot_id: 3290
    ├─ is_parent: FALSE
    └─ Show as sub-listing or hide from main search
```

**Frontend Display:**
- Main search shows only parent spots (is_parent = TRUE OR parent_spot_id IS NULL)
- Individual spot pages show all child water bodies
- Detail page lists all ponds at the location

#### Option 2: JSON Array in Single Spot (Alternative)

**Database Changes:**
```sql
ALTER TABLE fishing_spots ADD COLUMN water_bodies JSON NULL;
```

**Example:**
```json
{
  "id": 3290,
  "name": "Jesse H. Jones Park and Nature Center",
  "water_bodies": [
    {
      "name": "Salad Bowl Pond",
      "water_type": "pond",
      "stocked_species": ["catfish", "bass"]
    },
    {
      "name": "Jones Youth Fishing Lake",
      "water_type": "lake",
      "stocked_species": ["catfish"]
    }
  ]
}
```

**Pros**: Simpler queries, single spot per location
**Cons**: Harder to track individual pond data, less flexible

## Implementation Plan

### Phase 1: Identify Consolidation Candidates

```python
def find_consolidation_candidates():
    """
    Find spots that should be consolidated:
    1. Same address
    2. Same spot_type (public_water, state_park)
    3. Different water_body_name
    """
    cur.execute("""
        SELECT address, COUNT(*) as count,
               GROUP_CONCAT(id) as ids,
               GROUP_CONCAT(water_body_name SEPARATOR ' | ') as water_bodies
        FROM fishing_spots
        WHERE address IS NOT NULL
          AND address != ''
          AND spot_type IN ('public_water', 'state_park')
        GROUP BY address
        HAVING COUNT(*) > 1
    """)
    return cur.fetchall()
```

### Phase 2: Create Parent Spots

For each address with multiple spots:

1. **Determine which spot should be the parent:**
   - If one has a park name (without specific pond name) → that's the parent
   - If all are pond names → create new parent with park name
   - If one is state_park type → that's the parent

2. **Set parent-child relationships:**
```python
# Example: Jesse H Jones
parent_id = 3290  # Jesse H. Jones Park and Nature Center
child_ids = [2641, 2647]  # Individual ponds

cur.execute("UPDATE fishing_spots SET is_parent = TRUE WHERE id = %s", (parent_id,))
for child_id in child_ids:
    cur.execute("""
        UPDATE fishing_spots
        SET parent_spot_id = %s, is_parent = FALSE
        WHERE id = %s
    """, (parent_id, child_id))
```

3. **Update parent description to list all water bodies:**
```python
parent_desc = "Park with multiple fishing ponds: Salad Bowl Pond and Jones Youth Fishing Lake. Regularly stocked by TPWD."
```

### Phase 3: Update API/Frontend

**API Changes** ([spots.php](../backend/api/spots.php)):
```php
// Only return parent spots by default
$query = "SELECT * FROM fishing_spots
          WHERE (is_parent = TRUE OR parent_spot_id IS NULL)
          AND state = 'TX'";

// On detail page, include children
$query = "SELECT * FROM fishing_spots
          WHERE id = ? OR parent_spot_id = ?";
```

**Frontend Changes**:
- Main listing: Show only parents
- Detail page: Show all water bodies at that location
- Add "Multiple fishing ponds available" badge for parents with children

### Phase 4: Data Quality Rules

Add to pipeline validation:

```python
class ParkConsolidationRule:
    def validate_spot(self, spot):
        # Check if address matches existing spots
        existing = find_spots_by_address(spot['address'])

        if len(existing) > 0:
            # Decide if this is a child of existing parent
            # or if we need to create a new parent
            if should_be_child(spot, existing):
                spot['parent_spot_id'] = existing[0]['id']
                spot['is_parent'] = False
            elif should_create_parent(spot, existing):
                parent = create_parent_spot(spot, existing)
                spot['parent_spot_id'] = parent['id']
```

## Current Duplicate Addresses to Fix

Based on current data, these need consolidation:

1. **Resoft Park Lake** - 2 duplicates (IDs 2315, 3252)
2. **Eldridge Park Pond** - 2 duplicates (IDs 2554, 3242)
3. **Kitty Hollow Lake** - 2 duplicates (IDs 2559, 3248)
4. **Seabourne Creek Park** - 2 duplicates (IDs 2565, 3253)
5. **Burke-Crenshaw Lake** - 2 duplicates (IDs 2622, 3236)
6. **Challenger 7 Pond** - 2 duplicates (IDs 2624, 3239)
7. **Eisenhower Park Pond** - 2 duplicates (IDs 2629, 3241)
8. **Mary Jo Peckham Park** - 2 duplicates (IDs 2642, 3250)
9. **Carl Barton Jr. Park Pond** - 2 duplicates (IDs 2805, 3238)
10. **City Lake Park (Mesquite)** - 2 duplicates (IDs 3020, 3265)
11. **Espada/South Side Lions** - Different names, same bad address (IDs 3274, 3275)

**Immediate Fix**: Delete the duplicates (keep one with better data)
**Long-term**: Implement parent-child system for true multi-pond parks

## Benefits

- ✅ **Cleaner search results** - One listing per location
- ✅ **Better UX** - Users aren't confused by duplicates
- ✅ **Preserve species data** - Can still track which pond has which fish
- ✅ **Flexible** - Can add new ponds to existing parks easily
- ✅ **Scalable** - Works for parks with 2-10+ ponds
- ✅ **Maintains data integrity** - Original data preserved for analysis

## Migration Script

```python
# 1. Add new columns
ALTER TABLE fishing_spots ADD COLUMN parent_spot_id INT NULL;
ALTER TABLE fishing_spots ADD COLUMN is_parent BOOLEAN DEFAULT FALSE;

# 2. Fix current exact duplicates (delete redundant entries)
# 3. Create parent spots for multi-pond parks
# 4. Set parent_spot_id for children
# 5. Update API to filter by parent status
# 6. Update frontend to display children on detail pages
```

## Future Considerations

- Add API endpoint to get all ponds at a location: `/api/spots/{id}/water_bodies`
- Track species by individual pond
- Show stocking reports per pond
- Allow users to report catches per specific pond
