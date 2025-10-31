<?php
/**
 * API Endpoint: Get fish species votes for a spot
 *
 * GET /api/get-votes.php?spot_id=123
 */

require_once 'config.php';

set_cors_headers();
header('Content-Type: application/json');

// Validate spot_id parameter
$spot_id = filter_input(INPUT_GET, 'spot_id', FILTER_VALIDATE_INT);

if (!$spot_id) {
    send_json(['error' => 'Invalid or missing spot_id'], 400);
}

$conn = get_db_connection();

$stmt = $conn->prepare("
    SELECT vote_type, vote_count
    FROM spot_votes
    WHERE fishing_spot_id = ?
    ORDER BY vote_count DESC
");

$stmt->bind_param("i", $spot_id);
$stmt->execute();
$result = $stmt->get_result();

$votes = [];
while ($row = $result->fetch_assoc()) {
    $votes[] = [
        'species' => str_replace('_', ' ', ucwords($row['vote_type'], '_')),
        'vote_type' => $row['vote_type'],
        'count' => (int)$row['vote_count']
    ];
}

$stmt->close();
$conn->close();

send_json([
    'success' => true,
    'votes' => $votes
]);
?>
