-- Add 'lake' and 'public_water' to spot_type enum
-- Run with: mysql -u root -p fishing_directory < 004_add_lake_public_water_types.sql

ALTER TABLE fishing_spots
MODIFY COLUMN spot_type ENUM(
    'boat_ramp',
    'bank_fishing',
    'pier',
    'wade_fishing',
    'kayak_launch',
    'fishing_pier',
    'state_park',
    'lake',
    'public_water'
) NOT NULL;
