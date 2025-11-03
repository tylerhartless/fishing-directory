-- Migration: Add 'community_lake' to spot_type enum
--
-- Run this migration to support community fishing lakes
--
-- Usage:
--   mysql -u fishing_user -p fishing_directory < migrations/002_add_community_lake_type.sql

USE fishing_directory;

-- Add 'community_lake' to the spot_type enum
ALTER TABLE fishing_spots
MODIFY COLUMN spot_type ENUM(
    'boat_ramp',
    'bank_fishing',
    'pier',
    'wade_fishing',
    'kayak_launch',
    'fishing_pier',
    'state_park',
    'community_lake'
) NOT NULL;

-- Show updated schema
DESCRIBE fishing_spots;

SELECT CONCAT('Migration complete! Added community_lake to spot_type enum') AS status;
