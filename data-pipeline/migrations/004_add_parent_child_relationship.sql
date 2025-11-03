-- Migration: Add parent-child relationship for multi-pond parks
-- This allows consolidation of display while preserving individual pond data

-- Add new columns
ALTER TABLE fishing_spots
ADD COLUMN parent_spot_id INT NULL AFTER id,
ADD COLUMN is_parent BOOLEAN DEFAULT FALSE AFTER parent_spot_id;

-- Add index for parent lookups
ALTER TABLE fishing_spots
ADD INDEX idx_parent_spot (parent_spot_id);

-- Add foreign key constraint
ALTER TABLE fishing_spots
ADD CONSTRAINT fk_parent_spot
FOREIGN KEY (parent_spot_id) REFERENCES fishing_spots(id)
ON DELETE CASCADE;

-- Set Jesse H. Jones Park as parent with children
UPDATE fishing_spots SET is_parent = TRUE WHERE id = 3290;
UPDATE fishing_spots SET parent_spot_id = 3290, is_parent = FALSE WHERE id IN (2641, 2647);

-- Note: For rollback, use:
-- ALTER TABLE fishing_spots DROP FOREIGN KEY fk_parent_spot;
-- ALTER TABLE fishing_spots DROP INDEX idx_parent_spot;
-- ALTER TABLE fishing_spots DROP COLUMN parent_spot_id;
-- ALTER TABLE fishing_spots DROP COLUMN is_parent;
