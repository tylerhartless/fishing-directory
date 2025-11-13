-- Migration 003: Species Prevalence System (Heat List)
-- Adds master species list, potential species, and catch reporting with time-decay scoring

-- ============================================================================
-- 1. MASTER SPECIES TABLE
-- Defines all fish species for each region with priority order
-- ============================================================================
CREATE TABLE IF NOT EXISTS `master_species` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `common_name` VARCHAR(100) NOT NULL COMMENT 'Display name (e.g., "Largemouth Bass")',
  `scientific_name` VARCHAR(100) DEFAULT NULL COMMENT 'Scientific name (optional)',
  `region` VARCHAR(50) NOT NULL COMMENT 'State code (e.g., "TX")',
  `priority_order` INT NOT NULL COMMENT 'Sort order for backfill (1 = most common)',
  `icon` VARCHAR(10) DEFAULT '🐟' COMMENT 'Emoji icon for UI',
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY `unique_species_per_region` (`common_name`, `region`),
  INDEX `idx_region_priority` (`region`, `priority_order`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Master list of fish species by region with priority ordering';

-- ============================================================================
-- 2. POTENTIAL SPECIES TABLE (Junction Table)
-- Links fishing spots to their potential species list
-- Populated automatically when a spot is created based on its state
-- ============================================================================
CREATE TABLE IF NOT EXISTS `potential_species` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `fishing_spot_id` INT NOT NULL,
  `master_species_id` INT NOT NULL,
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (`fishing_spot_id`) REFERENCES `fishing_spots`(`id`) ON DELETE CASCADE,
  FOREIGN KEY (`master_species_id`) REFERENCES `master_species`(`id`) ON DELETE CASCADE,
  UNIQUE KEY `unique_spot_species` (`fishing_spot_id`, `master_species_id`),
  INDEX `idx_spot_id` (`fishing_spot_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Links spots to their geographically relevant species';

-- ============================================================================
-- 3. CATCH REPORTS TABLE
-- User-submitted catch data with time-decay scoring
-- ============================================================================
CREATE TABLE IF NOT EXISTS `catch_reports` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `fishing_spot_id` INT NOT NULL,
  `master_species_id` INT NOT NULL,
  `user_ip_hash` VARCHAR(64) NOT NULL COMMENT 'Hashed IP for rate limiting',
  `catch_date` DATE NOT NULL COMMENT 'When the fish was caught',
  `base_score` DECIMAL(10,2) DEFAULT 10.00 COMMENT 'Initial points (default: 10)',
  `current_score` DECIMAL(10,2) DEFAULT 10.00 COMMENT 'Score after time-decay',
  `last_decay_date` DATE NOT NULL COMMENT 'Last time decay was applied',
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (`fishing_spot_id`) REFERENCES `fishing_spots`(`id`) ON DELETE CASCADE,
  FOREIGN KEY (`master_species_id`) REFERENCES `master_species`(`id`) ON DELETE CASCADE,
  INDEX `idx_spot_species` (`fishing_spot_id`, `master_species_id`),
  INDEX `idx_decay_date` (`last_decay_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Catch reports with time-decay scoring for prevalence calculation';

-- ============================================================================
-- 4. PREVALENCE SCORES VIEW (Materialized via query)
-- Aggregates current_score by spot and species for fast lookups
-- ============================================================================
-- This is a commonly-used query pattern that could be materialized later
-- For now, we'll query it directly in the API:
--
-- SELECT
--   cr.fishing_spot_id,
--   cr.master_species_id,
--   ms.common_name,
--   ms.icon,
--   SUM(cr.current_score) as total_score,
--   COUNT(*) as report_count,
--   CASE
--     WHEN SUM(cr.current_score) >= 5000 THEN 'common'
--     WHEN SUM(cr.current_score) >= 1000 THEN 'uncommon'
--     WHEN SUM(cr.current_score) > 0 THEN 'rare'
--     ELSE 'unreported'
--   END as tier
-- FROM catch_reports cr
-- JOIN master_species ms ON cr.master_species_id = ms.id
-- WHERE cr.fishing_spot_id = ?
-- GROUP BY cr.fishing_spot_id, cr.master_species_id
-- ORDER BY total_score DESC

-- ============================================================================
-- 5. POPULATE MASTER SPECIES FOR TEXAS
-- Top 30 most common fish species in Texas with priority order
-- ============================================================================
INSERT INTO `master_species` (`common_name`, `scientific_name`, `region`, `priority_order`, `icon`) VALUES
-- Top Tier Game Fish (Priority 1-10)
('Largemouth Bass', 'Micropterus salmoides', 'TX', 1, '🎣'),
('Channel Catfish', 'Ictalurus punctatus', 'TX', 2, '🐡'),
('Bluegill', 'Lepomis macrochirus', 'TX', 3, '🐟'),
('White Crappie', 'Pomoxis annularis', 'TX', 4, '🐠'),
('Redear Sunfish', 'Lepomis microlophus', 'TX', 5, '🐟'),
('White Bass', 'Morone chrysops', 'TX', 6, '🎣'),
('Striped Bass', 'Morone saxatilis', 'TX', 7, '🎣'),
('Blue Catfish', 'Ictalurus furcatus', 'TX', 8, '🐡'),
('Black Crappie', 'Pomoxis nigromaculatus', 'TX', 9, '🐠'),
('Flathead Catfish', 'Pylodictis olivaris', 'TX', 10, '🐡'),

-- Common Sunfish & Panfish (Priority 11-15)
('Longear Sunfish', 'Lepomis megalotis', 'TX', 11, '🐟'),
('Green Sunfish', 'Lepomis cyanellus', 'TX', 12, '🐟'),
('Warmouth', 'Lepomis gulosus', 'TX', 13, '🐟'),
('Hybrid Striped Bass', 'Morone saxatilis × chrysops', 'TX', 14, '🎣'),
('Yellow Bass', 'Morone mississippiensis', 'TX', 15, '🐟'),

-- Other Bass Species (Priority 16-20)
('Spotted Bass', 'Micropterus punctulatus', 'TX', 16, '🎣'),
('Smallmouth Bass', 'Micropterus dolomieu', 'TX', 17, '🎣'),
('Guadalupe Bass', 'Micropterus treculii', 'TX', 18, '🎣'),
('White Crappie', 'Pomoxis annularis', 'TX', 19, '🐠'),

-- Rough Fish & Other Species (Priority 20-30)
('Common Carp', 'Cyprinus carpio', 'TX', 20, '🐟'),
('Freshwater Drum', 'Aplodinotus grunniens', 'TX', 21, '🐟'),
('Alligator Gar', 'Atractosteus spatula', 'TX', 22, '🦈'),
('Longnose Gar', 'Lepisosteus osseus', 'TX', 23, '🦈'),
('Spotted Gar', 'Lepisosteus oculatus', 'TX', 24, '🦈'),
('Gizzard Shad', 'Dorosoma cepedianum', 'TX', 25, '🐟'),
('Threadfin Shad', 'Dorosoma petenense', 'TX', 26, '🐟'),
('Rio Grande Cichlid', 'Herichthys cyanoguttatus', 'TX', 27, '🐠'),
('Bowfin', 'Amia calva', 'TX', 28, '🐟'),
('Buffalo Species', 'Ictiobus spp.', 'TX', 29, '🐟'),
('Rainbow Trout', 'Oncorhynchus mykiss', 'TX', 30, '🐟')
ON DUPLICATE KEY UPDATE
  `priority_order` = VALUES(`priority_order`),
  `icon` = VALUES(`icon`);

-- ============================================================================
-- 6. POPULATE POTENTIAL SPECIES FOR EXISTING SPOTS
-- Link all Texas spots to the full master species list
-- ============================================================================
INSERT INTO `potential_species` (`fishing_spot_id`, `master_species_id`)
SELECT
  fs.id as fishing_spot_id,
  ms.id as master_species_id
FROM fishing_spots fs
CROSS JOIN master_species ms
WHERE fs.state = 'TX'
  AND ms.region = 'TX'
  AND NOT EXISTS (
    SELECT 1 FROM potential_species ps
    WHERE ps.fishing_spot_id = fs.id
      AND ps.master_species_id = ms.id
  );

-- ============================================================================
-- 7. CREATE TRIGGER TO AUTO-POPULATE POTENTIAL SPECIES FOR NEW SPOTS
-- When a new fishing spot is created, automatically link it to master species
-- ============================================================================
DELIMITER $$

CREATE TRIGGER `auto_populate_potential_species`
AFTER INSERT ON `fishing_spots`
FOR EACH ROW
BEGIN
  INSERT INTO `potential_species` (`fishing_spot_id`, `master_species_id`)
  SELECT
    NEW.id,
    ms.id
  FROM master_species ms
  WHERE ms.region = NEW.state;
END$$

DELIMITER ;

-- ============================================================================
-- MIGRATION COMPLETE
-- ============================================================================
-- Next Steps:
-- 1. Apply this migration: mysql -u user -p fishing_directory < 003_species_prevalence_system.sql
-- 2. Create backend API endpoints (log-catch.php, get-heat-list.php)
-- 3. Create time-decay cron script (decay-scores.php)
-- 4. Update frontend UI components
-- ============================================================================
