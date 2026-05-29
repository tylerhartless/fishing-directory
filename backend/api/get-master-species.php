<?php
/**
 * API Endpoint: Get the full master species list for the Log a Catch modal.
 *
 * GET /api/get-master-species.php
 * GET /api/get-master-species.php?region=TX  (optional)
 *
 * Returns every species in master_species, ordered by priority. The frontend's
 * Log a Catch dropdown should always show the full picker regardless of what's
 * been reported at the current spot.
 */

require_once 'config.php';

set_cors_headers();
header('Content-Type: application/json');

if ($_SERVER['REQUEST_METHOD'] !== 'GET') {
    send_json(['error' => 'Method not allowed'], 405);
}

$region = trim($_GET['region'] ?? '');
$conn = get_db_connection();

if ($region !== '' && preg_match('/^[A-Za-z]{2}$/', $region)) {
    $stmt = $conn->prepare("
        SELECT id, common_name, icon, priority_order, region
        FROM master_species
        WHERE region = ?
        ORDER BY priority_order ASC
    ");
    $regionUpper = strtoupper($region);
    $stmt->bind_param('s', $regionUpper);
} else {
    $stmt = $conn->prepare("
        SELECT id, common_name, icon, priority_order, region
        FROM master_species
        ORDER BY region ASC, priority_order ASC
    ");
}

$stmt->execute();
$result = $stmt->get_result();

$species = [];
while ($row = $result->fetch_assoc()) {
    $species[] = [
        'id' => intval($row['id']),
        'common_name' => $row['common_name'],
        'icon' => $row['icon'],
        'priority_order' => intval($row['priority_order']),
        'region' => $row['region'],
    ];
}

$stmt->close();
$conn->close();

send_json([
    'success' => true,
    'species' => $species,
]);
