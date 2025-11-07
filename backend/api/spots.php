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

// Build query - join with counties for multi-county support
$query = "SELECT
    fs.id,
    fs.name,
    fs.slug,
    fs.latitude,
    fs.longitude,
    fs.county,
    fs.state,
    fs.water_body_name,
    fs.spot_type,
    fs.address,
    fs.description,
    fs.amenities,
    fs.parent_spot_id,
    fs.is_parent,
    GROUP_CONCAT(c.name ORDER BY sc.is_primary DESC, c.name ASC SEPARATOR '|') as counties_list
FROM fishing_spots fs
LEFT JOIN spot_counties sc ON fs.id = sc.fishing_spot_id
LEFT JOIN counties c ON sc.county_id = c.id
WHERE 1=1";

$params = [];
$types = '';

// Only show parent spots or spots without parents (hide child spots from main listing)
$query .= " AND (fs.is_parent = TRUE OR fs.parent_spot_id IS NULL)";

// Exclude boat ramps by default unless explicitly requested
if (!$includeBoatRamps) {
    $query .= " AND fs.spot_type != 'boat_ramp'";
}

// County filtering - supports both legacy single county and new multi-county
if ($county) {
    // Check if spot is in the county using either legacy field or junction table
    $query .= " AND (fs.county = ? OR c.name = ?)";
    $params[] = $county;
    $params[] = $county;
    $types .= 'ss';
}

$query .= " GROUP BY fs.id ORDER BY fs.name ASC LIMIT ?";
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
    // Convert counties_list string to array
    if (!empty($row['counties_list'])) {
        $row['counties'] = explode('|', $row['counties_list']);
    } else {
        $row['counties'] = [];
    }

    // Remove the temporary counties_list field
    unset($row['counties_list']);

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