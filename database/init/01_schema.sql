-- Initial schema for fresh fishing_directory database.
-- Reflects post-migration-004 state: canonical spots live in
-- data/publish/<state>/spots.json; only master_species (vocabulary)
-- and catch_reports (user data, keyed by canonical_id) persist in MySQL.

-- ============================================================================
-- master_species — controlled vocabulary for catch reports
-- ============================================================================
CREATE TABLE IF NOT EXISTS `master_species` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `common_name` VARCHAR(100) NOT NULL,
  `scientific_name` VARCHAR(100) DEFAULT NULL,
  `region` VARCHAR(50) NOT NULL,
  `priority_order` INT NOT NULL,
  `icon` VARCHAR(10) DEFAULT '🐟',
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY `unique_species_per_region` (`common_name`, `region`),
  INDEX `idx_region_priority` (`region`, `priority_order`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO `master_species` (`common_name`, `scientific_name`, `region`, `priority_order`, `icon`) VALUES
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
('Longear Sunfish', 'Lepomis megalotis', 'TX', 11, '🐟'),
('Green Sunfish', 'Lepomis cyanellus', 'TX', 12, '🐟'),
('Warmouth', 'Lepomis gulosus', 'TX', 13, '🐟'),
('Hybrid Striped Bass', 'Morone saxatilis × chrysops', 'TX', 14, '🎣'),
('Yellow Bass', 'Morone mississippiensis', 'TX', 15, '🐟'),
('Spotted Bass', 'Micropterus punctulatus', 'TX', 16, '🎣'),
('Smallmouth Bass', 'Micropterus dolomieu', 'TX', 17, '🎣'),
('Guadalupe Bass', 'Micropterus treculii', 'TX', 18, '🎣'),
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
-- catch_reports — keyed by canonical_id string from publish JSON
-- ============================================================================
CREATE TABLE IF NOT EXISTS `catch_reports` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `canonical_id` VARCHAR(64) NOT NULL,
  `master_species_id` INT NOT NULL,
  `user_ip_hash` VARCHAR(64) NOT NULL,
  `catch_date` DATE NOT NULL,
  `base_score` DECIMAL(10,2) DEFAULT 10.00,
  `current_score` DECIMAL(10,2) DEFAULT 10.00,
  `last_decay_date` DATE NOT NULL,
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (`master_species_id`) REFERENCES `master_species`(`id`) ON DELETE CASCADE,
  INDEX `idx_canonical_species` (`canonical_id`, `master_species_id`),
  INDEX `idx_decay_date` (`last_decay_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
