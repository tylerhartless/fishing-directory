<?php
/**
 * API Endpoint: Get county statistics
 *
 * GET /api/county-stats.php?state=TX&limit=10
 *
 * Returns counties with spot counts in JSON format
 */

require_once 'config.php';

set_cors_headers();
header('Content-Type: application/json');

// Get parameters
$state = isset($_GET['state']) ? strtoupper(htmlspecialchars($_GET['state'], ENT_QUOTES, 'UTF-8')) : 'TX';
$limit = filter_input(INPUT_GET, 'limit', FILTER_VALIDATE_INT) ?: 10;

// Validate state code (2 letters)
if (strlen($state) !== 2 || !ctype_alpha($state)) {
    send_json(['error' => 'Invalid state code'], 400);
}

$conn = get_db_connection();

// Check if the new many-to-many tables exist (post-migration)
$tablesExist = false;
$checkTables = $conn->query("SHOW TABLES LIKE 'spot_counties'");
if ($checkTables && $checkTables->num_rows > 0) {
    $tablesExist = true;
}

if ($tablesExist) {
    // POST-MIGRATION: Use many-to-many relationship with counties
    $query = "SELECT
        c.id,
        c.name,
        c.slug,
        c.state,
        COUNT(DISTINCT fs.id) as spot_count
    FROM counties c
    LEFT JOIN spot_counties sc ON c.id = sc.county_id
    LEFT JOIN fishing_spots fs ON sc.fishing_spot_id = fs.id
        AND (fs.is_parent = TRUE OR fs.parent_spot_id IS NULL)
        AND fs.spot_type != 'boat_ramp'
    WHERE c.state = ?
    GROUP BY c.id, c.name, c.slug, c.state
    HAVING spot_count > 0
    ORDER BY spot_count DESC, c.name ASC
    LIMIT ?";

    $stmt = $conn->prepare($query);
    $stmt->bind_param('si', $state, $limit);
} else {
    // PRE-MIGRATION: Use legacy single county field
    $query = "SELECT
        county as name,
        LOWER(REPLACE(TRIM(county), ' ', '-')) as slug,
        ? as state,
        COUNT(*) as spot_count
    FROM fishing_spots
    WHERE state = ?
        AND county IS NOT NULL
        AND county != ''
        AND county != 'Multiple Counties'
        AND (is_parent = TRUE OR parent_spot_id IS NULL)
        AND spot_type != 'boat_ramp'
    GROUP BY county
    ORDER BY spot_count DESC, county ASC
    LIMIT ?";

    $stmt = $conn->prepare($query);
    $stmt->bind_param('ssi', $state, $state, $limit);
}

$stmt->execute();
$result = $stmt->get_result();

$counties = [];
while ($row = $result->fetch_assoc()) {
    $counties[] = [
        'name' => $row['name'],
        'slug' => $row['slug'],
        'state' => $row['state'],
        'spot_count' => (int)$row['spot_count']
    ];
}

$stmt->close();
$conn->close();

// Return results
send_json([
    'success' => true,
    'state' => $state,
    'count' => count($counties),
    'counties' => $counties
]);
?>
