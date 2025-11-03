-- Migration: Refactor spot_type to use generic, nationwide categories
--
-- Changes community_lake to public_lake for better nationwide compatibility
--
-- Usage:
--   Run via Python db_utils or directly:
--   mysql -u fishing_user -p fishing_directory < migrations/003_refactor_spot_types.sql

USE fishing_directory;

-- First, add new generic types to enum
ALTER TABLE fishing_spots
MODIFY COLUMN spot_type ENUM(
    'boat_ramp',
    'bank_fishing',
    'pier',
    'wade_fishing',
    'kayak_launch',
    'fishing_pier',
    'state_park',
    'community_lake',  -- Keep temporarily for migration
    'public_lake',     -- NEW: Generic public lakes/ponds
    'urban_fishing',   -- NEW: Urban parks and neighborhood lakes
    'wildlife_area'    -- NEW: Wildlife management areas
) NOT NULL;

-- Migrate existing community_lake records to public_lake
UPDATE fishing_spots
SET spot_type = 'public_lake'
WHERE spot_type = 'community_lake';

-- Now remove community_lake from enum
ALTER TABLE fishing_spots
MODIFY COLUMN spot_type ENUM(
    'boat_ramp',
    'bank_fishing',
    'pier',
    'wade_fishing',
    'kayak_launch',
    'fishing_pier',
    'state_park',
    'public_lake',
    'urban_fishing',
    'wildlife_area'
) NOT NULL;

-- Show results
SELECT spot_type, COUNT(*) as count
FROM fishing_spots
GROUP BY spot_type
ORDER BY count DESC;

SELECT CONCAT('Migration complete! Converted community_lake -> public_lake') AS status;
