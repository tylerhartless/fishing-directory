-- Migration: Add many-to-many relationship for spots and counties
-- Date: 2025-11-07
-- Ticket: TICKET-034

-- Step 1: Create counties reference table
CREATE TABLE IF NOT EXISTS `counties` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `state` varchar(2) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'TX',
  `slug` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_county_state` (`name`, `state`),
  UNIQUE KEY `unique_slug` (`slug`),
  KEY `idx_state` (`state`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Reference table for all Texas counties';

-- Step 2: Create junction table for many-to-many relationship
CREATE TABLE IF NOT EXISTS `spot_counties` (
  `id` int NOT NULL AUTO_INCREMENT,
  `fishing_spot_id` int NOT NULL,
  `county_id` int NOT NULL,
  `is_primary` tinyint(1) DEFAULT '1' COMMENT 'Mark the primary county for spots that span multiple',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_spot_county` (`fishing_spot_id`, `county_id`),
  KEY `idx_spot` (`fishing_spot_id`),
  KEY `idx_county` (`county_id`),
  KEY `idx_primary` (`is_primary`),
  CONSTRAINT `fk_spot_counties_spot` FOREIGN KEY (`fishing_spot_id`)
    REFERENCES `fishing_spots` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_spot_counties_county` FOREIGN KEY (`county_id`)
    REFERENCES `counties` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Junction table linking fishing spots to multiple counties';

-- Step 3: Populate counties table with existing unique counties from fishing_spots
INSERT INTO `counties` (`name`, `state`, `slug`)
SELECT DISTINCT
  TRIM(county) as name,
  'TX' as state,
  LOWER(REPLACE(TRIM(county), ' ', '-')) as slug
FROM `fishing_spots`
WHERE county IS NOT NULL
  AND county != ''
  AND county != 'Multiple Counties'
ORDER BY county
ON DUPLICATE KEY UPDATE name = name; -- No-op on duplicate

-- Step 4: Populate junction table with existing single-county relationships
-- This preserves all current spot-county associations
INSERT INTO `spot_counties` (`fishing_spot_id`, `county_id`, `is_primary`)
SELECT
  fs.id,
  c.id,
  1 as is_primary
FROM `fishing_spots` fs
INNER JOIN `counties` c ON TRIM(fs.county) = c.name
WHERE fs.county != 'Multiple Counties'
  AND fs.county IS NOT NULL
  AND fs.county != ''
ON DUPLICATE KEY UPDATE is_primary = is_primary; -- No-op on duplicate

-- Step 5: Keep the county column for backward compatibility
-- We'll deprecate it later once all code is updated
-- For now, it will store either the primary county or 'Multiple Counties'
ALTER TABLE `fishing_spots`
MODIFY COLUMN `county` varchar(100) COLLATE utf8mb4_unicode_ci NULL
COMMENT 'DEPRECATED: Use spot_counties junction table. Kept for backward compatibility.';

-- Step 6: Add index to help with legacy queries
CREATE INDEX `idx_county_legacy` ON `fishing_spots` (`county`);

-- Verification queries (run these manually to verify migration):
-- SELECT COUNT(*) FROM counties; -- Should show ~254 Texas counties
-- SELECT COUNT(*) FROM spot_counties; -- Should match non-Multiple Counties spots
-- SELECT fs.name, GROUP_CONCAT(c.name) as counties
-- FROM fishing_spots fs
-- LEFT JOIN spot_counties sc ON fs.id = sc.fishing_spot_id
-- LEFT JOIN counties c ON sc.county_id = c.id
-- GROUP BY fs.id
-- LIMIT 10;
