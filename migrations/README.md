# Database Migrations

This directory contains SQL migration scripts for the Fishing Directory database.

## Migration 002: County Many-to-Many Relationship

**File:** `002_county_many_to_many.sql`
**Date:** 2025-11-07
**Ticket:** TICKET-034

### Overview

This migration adds support for fishing spots that span multiple counties by introducing a many-to-many relationship between `fishing_spots` and a new `counties` reference table.

### What Changes

#### New Tables

1. **`counties`** - Reference table for all Texas counties
   - `id` - Primary key
   - `name` - County name (e.g., "Travis")
   - `state` - State code (default: "TX")
   - `slug` - URL-friendly slug (e.g., "travis")
   - Unique constraint on `(name, state)` combination

2. **`spot_counties`** - Junction table linking spots to counties
   - `id` - Primary key
   - `fishing_spot_id` - Foreign key to `fishing_spots.id`
   - `county_id` - Foreign key to `counties.id`
   - `is_primary` - Boolean flag marking the primary county for multi-county spots
   - Unique constraint on `(fishing_spot_id, county_id)` combination

#### Modified Tables

- **`fishing_spots.county`** - Column kept for backward compatibility but deprecated
  - Now nullable
  - Should be considered legacy - use `spot_counties` junction table instead

### Running the Migration

```bash
# Connect to your MySQL database
mysql -u your_user -p your_database < migrations/002_county_many_to_many.sql
```

### What the Migration Does

1. Creates `counties` reference table
2. Creates `spot_counties` junction table
3. Populates `counties` with all unique counties from existing spots (except "Multiple Counties" placeholder)
4. Populates `spot_counties` with existing single-county relationships
5. Marks the legacy `county` column as deprecated
6. Adds helpful indexes for queries

### Post-Migration

After running this migration:

- **All existing spots** will have their county relationships preserved in the junction table
- **177 spots** currently marked as "Multiple Counties" will need to be mapped to their actual counties
- The legacy `county` column remains intact for backward compatibility
- New code should use the `counties` array returned by the API

### API Changes

The `spots.php` API now returns a `counties` array for each spot:

```json
{
  "id": 123,
  "name": "Lake Travis",
  "county": "Travis",  // Legacy field - deprecated
  "counties": ["Travis", "Burnet"],  // New field - use this!
  ...
}
```

### Frontend Changes

The TypeScript `FishingSpot` interface now includes:

```typescript
interface FishingSpot {
  county: string;      // DEPRECATED: Legacy field
  counties?: string[]; // NEW: Array of counties
  ...
}
```

Helper functions have been added to `database.ts`:

- `getSpotCounties(spot)` - Returns array of all counties for a spot
- `spotIsInCounty(spot, countyName)` - Checks if spot is in a given county
- `getSpotCountyDisplay(spot)` - Returns formatted display string (e.g., "Travis & Burnet")

### Updating "Multiple Counties" Spots

The 177 spots currently marked as "Multiple Counties" need their actual counties mapped. This will be done as part of the data pipeline work (future ticket).

To find these spots:

```sql
SELECT id, name, slug, water_body_name
FROM fishing_spots
WHERE county = 'Multiple Counties'
ORDER BY name;
```

### Backward Compatibility

- The legacy `county` field is preserved and still works
- Old API calls continue to return the `county` field
- Frontend code using `getSpotsByCounty()` automatically works with both formats
- No breaking changes to existing functionality

### Verification Queries

```sql
-- Count counties
SELECT COUNT(*) as county_count FROM counties;

-- Count spot-county relationships
SELECT COUNT(*) as relationship_count FROM spot_counties;

-- View multi-county spots
SELECT
  fs.id,
  fs.name,
  GROUP_CONCAT(c.name ORDER BY sc.is_primary DESC) as counties
FROM fishing_spots fs
INNER JOIN spot_counties sc ON fs.id = sc.fishing_spot_id
INNER JOIN counties c ON sc.county_id = c.id
GROUP BY fs.id
HAVING COUNT(*) > 1;

-- Spots still needing county mapping
SELECT COUNT(*)
FROM fishing_spots
WHERE county = 'Multiple Counties'
  AND id NOT IN (SELECT fishing_spot_id FROM spot_counties);
```

### Rollback

To rollback this migration:

```sql
-- Drop junction table and foreign keys
DROP TABLE IF EXISTS spot_counties;

-- Drop counties table
DROP TABLE IF EXISTS counties;

-- Restore county column (remove deprecation comment)
ALTER TABLE fishing_spots
MODIFY COLUMN county varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL;
```

**Note:** This rollback will lose any newly mapped multi-county relationships.
