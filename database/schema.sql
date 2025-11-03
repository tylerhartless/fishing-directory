-- =====================================================
-- Texas Fishing Directory - Database Schema
-- =====================================================

-- Drop existing tables (careful in production!)
DROP TABLE IF EXISTS fishing_reports;
DROP TABLE IF EXISTS spot_votes;
DROP TABLE IF EXISTS fish_habitat_structures;
DROP TABLE IF EXISTS fishing_spots;

-- =====================================================
-- Main Table: fishing_spots
-- =====================================================
CREATE TABLE fishing_spots (
    id INT AUTO_INCREMENT PRIMARY KEY,

    -- Basic Information
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(255) NOT NULL UNIQUE,

    -- Location Data
    latitude DECIMAL(10, 7) NOT NULL,
    longitude DECIMAL(11, 7) NOT NULL,
    county VARCHAR(100) NOT NULL,
    water_body_name VARCHAR(255),

    -- Classification
    spot_type ENUM(
        'boat_ramp',
        'bank_fishing',
        'pier',
        'wade_fishing',
        'kayak_launch',
        'fishing_pier',
        'state_park',
        'lake',
        'public_water',
        'river_access'
    ) NOT NULL,

    -- Details
    description TEXT,
    amenities JSON COMMENT 'Stores: parking, restrooms, lighting, fish_cleaning, camping, etc.',

    -- Metadata
    data_source VARCHAR(100) COMMENT 'e.g., TPWD_Boat_Ramps, User_Submission, RACA',
    is_verified BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,

    -- SEO Fields
    meta_title VARCHAR(255),
    meta_description VARCHAR(320),

    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    -- Indexes for performance
    INDEX idx_county (county),
    INDEX idx_spot_type (spot_type),
    INDEX idx_location (latitude, longitude),
    INDEX idx_verified (is_verified, is_active),
    FULLTEXT INDEX idx_search (name, description)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =====================================================
-- Fish Habitat Structures (underwater attractors)
-- =====================================================
CREATE TABLE fish_habitat_structures (
    id INT AUTO_INCREMENT PRIMARY KEY,
    fishing_spot_id INT NOT NULL,

    structure_type ENUM(
        'tire_reef',
        'brush_pile',
        'concrete_structure',
        'pvc_attractor',
        'natural_structure',
        'unknown'
    ) DEFAULT 'unknown',

    latitude DECIMAL(10, 7),
    longitude DECIMAL(11, 7),
    depth_range VARCHAR(50) COMMENT 'e.g., 15-20 feet',

    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (fishing_spot_id) REFERENCES fishing_spots(id) ON DELETE CASCADE,
    INDEX idx_spot (fishing_spot_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =====================================================
-- User-Submitted Fishing Reports
-- =====================================================
CREATE TABLE fishing_reports (
    id INT AUTO_INCREMENT PRIMARY KEY,
    fishing_spot_id INT NOT NULL,

    -- Privacy-conscious tracking
    user_ip_hash VARCHAR(64) COMMENT 'SHA-256 hash for rate limiting, not storing actual IP',

    -- Report Data
    fish_species VARCHAR(100) NOT NULL,
    catch_count INT DEFAULT 1,
    report_date DATE NOT NULL,
    notes TEXT,

    -- Moderation
    is_approved BOOLEAN DEFAULT FALSE,
    reviewed_at TIMESTAMP NULL,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (fishing_spot_id) REFERENCES fishing_spots(id) ON DELETE CASCADE,
    INDEX idx_spot_approved (fishing_spot_id, is_approved),
    INDEX idx_report_date (report_date),
    INDEX idx_ip_hash (user_ip_hash, created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =====================================================
-- Voting System: What fish are at this spot?
-- =====================================================
CREATE TABLE spot_votes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    fishing_spot_id INT NOT NULL,

    vote_type ENUM(
        'largemouth_bass',
        'striped_bass',
        'white_bass',
        'catfish',
        'crappie',
        'sunfish',
        'carp',
        'gar',
        'trout',
        'redfish',
        'flounder'
    ) NOT NULL,

    vote_count INT DEFAULT 0,
    last_voted TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    FOREIGN KEY (fishing_spot_id) REFERENCES fishing_spots(id) ON DELETE CASCADE,
    UNIQUE KEY unique_spot_vote (fishing_spot_id, vote_type),
    INDEX idx_spot (fishing_spot_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =====================================================
-- Sample Data (for testing)
-- =====================================================
INSERT INTO fishing_spots (
    name, slug, latitude, longitude, county, water_body_name,
    spot_type, description, amenities, data_source, is_verified
) VALUES (
    'Lake Conroe Boat Ramp #5',
    'lake-conroe-boat-ramp-5-montgomery',
    30.3158,
    -95.4555,
    'Montgomery',
    'Lake Conroe',
    'boat_ramp',
    'Popular boat ramp with easy access to Lake Conroe. Great for bass fishing.',
    JSON_OBJECT(
        'parking', true,
        'restrooms', true,
        'lighting', false,
        'fish_cleaning', true,
        'boat_trailer_parking', true
    ),
    'TPWD_Boat_Ramps',
    TRUE
);

-- Add sample vote data
INSERT INTO spot_votes (fishing_spot_id, vote_type, vote_count) VALUES
    (1, 'largemouth_bass', 45),
    (1, 'catfish', 23),
    (1, 'crappie', 12);

-- =====================================================
-- Useful Queries (for reference)
-- =====================================================

-- Find all spots in a county:
-- SELECT * FROM fishing_spots WHERE county = 'Harris' AND is_active = TRUE;

-- Get spots near a coordinate (requires spatial extension or app logic):
-- Use Haversine formula in application code or MySQL ST_Distance_Sphere

-- Get approved fishing reports for a spot:
-- SELECT * FROM fishing_reports
-- WHERE fishing_spot_id = 1 AND is_approved = TRUE
-- ORDER BY report_date DESC LIMIT 10;

-- Get fish species ranking for a spot:
-- SELECT vote_type, vote_count
-- FROM spot_votes
-- WHERE fishing_spot_id = 1
-- ORDER BY vote_count DESC;