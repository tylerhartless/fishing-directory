<?php
/**
 * API Endpoint: Get fishing spots
 *
 * GET /api/spots.php?limit=10&county=Anderson
 *
 * Returns fishing spots in JSON format
 */

require_once 'config.php';

set_cors_headers();
header('Content-Type: application/json');

// Get parameters
$limit = filter_input(INPUT_GET, 'limit', FILTER_VALIDATE_INT) ?: 10;
$county = isset($_GET['county']) ? htmlspecialchars($_GET['county'], ENT_QUOTES, 'UTF-8') : null;
$includeBoatRamps = isset($_GET['include_boat_ramps']) && $_GET['include_boat_ramps'] === 'true';

$conn = get_db_connection();

// Build query
$query = "SELECT
    id,
    name,
    slug,
    latitude,
    longitude,
    county,
    state,
    water_body_name,
    spot_type,
    address,
    description,
    amenities,
    parent_spot_id,
    is_parent
FROM fishing_spots WHERE 1=1";

$params = [];
$types = '';

// Only show parent spots or spots without parents (hide child spots from main listing)
$query .= " AND (is_parent = TRUE OR parent_spot_id IS NULL)";

// Exclude boat ramps by default unless explicitly requested
if (!$includeBoatRamps) {
    $query .= " AND spot_type != 'boat_ramp'";
}

if ($county) {
    $query .= " AND county = ?";
    $params[] = $county;
    $types .= 's';
}

$query .= " ORDER BY name ASC LIMIT ?";
$params[] = $limit;
$types .= 'i';

// Prepare and execute
$stmt = $conn->prepare($query);
if ($types) {
    $stmt->bind_param($types, ...$params);
}
$stmt->execute();
$result = $stmt->get_result();

$spots = [];
while ($row = $result->fetch_assoc()) {
    $spots[] = $row;
}

$stmt->close();
$conn->close();

// Return results
send_json([
    'success' => true,
    'count' => count($spots),
    'spots' => $spots
]);
?>