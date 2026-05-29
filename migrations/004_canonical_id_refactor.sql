-- Migration 004: Canonical ID refactor
--
-- Removes the legacy fishing_spots-as-source-of-truth schema. Canonical spots
-- now live in data/publish/<state>/spots.json (built into the Astro site at
-- build time). User-generated data (catch_reports) attaches by a string
-- canonical_id derived from {state}-{county-slug}-{name-slug}-{record-id-tail}.
--
-- Pre-launch: zero rows of catch_reports / fishing_reports exist anywhere.
-- This migration is destructive (DROP + recreate) — no backfill.

SET FOREIGN_KEY_CHECKS = 0;

DROP TABLE IF EXISTS `catch_reports`;
DROP TABLE IF EXISTS `fishing_reports`;
DROP TABLE IF EXISTS `potential_species`;
DROP TABLE IF EXISTS `spot_counties`;
DROP TABLE IF EXISTS `counties`;
DROP TABLE IF EXISTS `fishing_spots`;
-- master_species is retained as the controlled vocabulary for catch reports.

SET FOREIGN_KEY_CHECKS = 1;

-- ============================================================================
-- catch_reports — keyed by canonical_id string
-- ============================================================================
CREATE TABLE `catch_reports` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `canonical_id` VARCHAR(64) NOT NULL COMMENT 'Spot identifier from publish JSON: {state}-{county}-{name}-{record-id-tail}',
  `master_species_id` INT NOT NULL,
  `user_ip_hash` VARCHAR(64) NOT NULL COMMENT 'Hashed IP for rate limiting',
  `catch_date` DATE NOT NULL COMMENT 'When the fish was caught',
  `base_score` DECIMAL(10,2) DEFAULT 10.00 COMMENT 'Initial points (default: 10)',
  `current_score` DECIMAL(10,2) DEFAULT 10.00 COMMENT 'Score after time-decay',
  `last_decay_date` DATE NOT NULL COMMENT 'Last time decay was applied',
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (`master_species_id`) REFERENCES `master_species`(`id`) ON DELETE CASCADE,
  INDEX `idx_canonical_species` (`canonical_id`, `master_species_id`),
  INDEX `idx_decay_date` (`last_decay_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Catch reports with time-decay scoring for prevalence calculation';
