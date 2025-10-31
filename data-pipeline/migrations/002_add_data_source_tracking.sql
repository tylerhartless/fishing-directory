-- Migration: Add data source tracking for programmatic updates
--
-- This adds metadata to track where data came from and when to refresh it
--
-- Usage:
--   mysql -u fishing_user -p fishing_directory < migrations/002_add_data_source_tracking.sql

USE fishing_directory;

-- Create data_sources table to track each dataset
CREATE TABLE IF NOT EXISTS data_sources (
    id INT AUTO_INCREMENT PRIMARY KEY,
    source_name VARCHAR(100) UNIQUE NOT NULL,
    source_type ENUM('csv_download', 'api', 'web_scrape', 'manual') NOT NULL,
    source_url TEXT,
    download_instructions TEXT,
    update_frequency VARCHAR(50) COMMENT 'e.g., monthly, quarterly, annually',
    last_updated TIMESTAMP NULL,
    next_update_due DATE NULL,
    record_count INT DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_source_name (source_name),
    INDEX idx_next_update (next_update_due)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Add fields to fishing_spots for better tracking
ALTER TABLE fishing_spots
ADD COLUMN source_last_updated TIMESTAMP NULL AFTER data_source,
ADD COLUMN source_record_id VARCHAR(100) NULL AFTER source_last_updated COMMENT 'Original ID from source system for update matching';

-- Create index for faster lookups during updates
ALTER TABLE fishing_spots
ADD INDEX idx_source_record (data_source, source_record_id);

-- Insert known Texas data sources
INSERT INTO data_sources (source_name, source_type, source_url, download_instructions, update_frequency, notes) VALUES
('TPWD_Boat_Ramps', 'csv_download', 'https://tpwd.texas.gov/gis/resources/boat-access.phtml',
 'Visit URL, look for CSV/Shapefile download link. If not available, email gisdata@tpwd.texas.gov',
 'quarterly',
 'Primary boat ramp dataset. ~2,500 records. Check for updates every 3 months.'),

('Texas_State_Parks', 'manual', 'https://tpwd.texas.gov/state-parks/parks/find-a-park',
 'Filter parks with fishing amenity, manually collect coordinates and details',
 'annually',
 'State parks with fishing access. FREE fishing - no license required!'),

('TPWD_Community_Fishing_Lakes', 'web_scrape', 'https://tpwd.texas.gov/fishboat/fish/recreational/lakes/',
 'Scrape or manually collect data from Community Fishing Lakes section',
 'annually',
 'CFL lakes stocked by TPWD. Good urban access.'),

('TPWD_RACA', 'manual', 'https://tpwd.texas.gov/fishboat/fish/recreational/raca/',
 'River Access lease program. Download river-specific PDFs with access points',
 'annually',
 'Public access on private land through lease agreements.'),

('TPWD_Fish_Habitat_Structures', 'csv_download', 'https://tpwd.texas.gov/fishboat/fish/habitats/',
 'Download coordinates for fish attractors by lake. Start with Lake Fork, Sam Rayburn',
 'annually',
 'Underwater structures (tire reefs, brush piles). Good for bass fishing content.'),

('TPWD_Fishing_Piers', 'manual', 'https://tpwd.texas.gov/fishboat/fish/recreational/coastal/',
 'Compile from boat ramp data + coastal fishing pages',
 'annually',
 'Fixed piers, often lighted and handicap accessible.'),

('TPWD_Coastal_Access', 'manual', 'https://tpwd.texas.gov/fishboat/fish/recreational/coastal/',
 'Beach and bay access for wade fishing',
 'annually',
 'Gulf coast wade fishing access points.');

-- Show results
SELECT
    source_name,
    source_type,
    update_frequency,
    record_count
FROM data_sources
ORDER BY source_name;

SELECT CONCAT('Migration complete! Added data source tracking.') AS status;
