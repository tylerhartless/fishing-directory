-- Migration: Add state, address, and zip_code fields for nationwide expansion
--
-- Run this migration to support fishing spots from multiple states
--
-- Usage:
--   mysql -u fishing_user -p fishing_directory < migrations/001_add_state_fields.sql

USE fishing_directory;

-- Add state column (2-letter state code)
ALTER TABLE fishing_spots
ADD COLUMN state VARCHAR(2) DEFAULT 'TX' AFTER data_source,
ADD INDEX idx_state (state);

-- Add address fields
ALTER TABLE fishing_spots
ADD COLUMN address VARCHAR(255) DEFAULT NULL AFTER state,
ADD COLUMN zip_code VARCHAR(10) DEFAULT NULL AFTER address;

-- Update existing records to have TX state
UPDATE fishing_spots SET state = 'TX' WHERE state IS NULL OR state = '';

-- Show updated schema
DESCRIBE fishing_spots;

SELECT CONCAT('Migration complete! Added columns: state, address, zip_code') AS status;
