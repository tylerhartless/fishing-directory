<?php
/**
 * API Endpoint: Vote on fish species at a spot
 *
 * POST /api/vote.php
 *
 * Body (JSON):
 * {
 *   "spot_id": 123,
 *   "vote_type": "largemouth_bass"
 * }
 */

require_once 'config.php';

set_cors_headers();
header('Content-Type: application/json');

// Only accept POST requests
if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    send_json(['error' => 'Method not allowed'], 405);
}

// Parse JSON input
$input = json_decode(file_get_contents('php://input'), true);

if (!$input) {
    send_json(['error' => 'Invalid JSON'], 400);
}

// Validate inputs
$spot_id = filter_var($input['spot_id'] ?? null, FILTER_VALIDATE_INT);
$vote_type = trim($input['vote_type'] ?? '');

$valid_vote_types = [
    'largemouth_bass', 'striped_bass', 'white_bass', 'catfish',
    'crappie', 'sunfish', 'carp', 'gar', 'trout', 'redfish', 'flounder'
];

if (!$spot_id) {
    send_json(['error' => 'Invalid spot_id'], 400);
}

if (!in_array($vote_type, $valid_vote_types)) {
    send_json(['error' => 'Invalid vote_type'], 400);
}

$conn = get_db_connection();

// Insert or increment vote count
$stmt = $conn->prepare("
    INSERT INTO spot_votes (fishing_spot_id, vote_type, vote_count)
    VALUES (?, ?, 1)
    ON DUPLICATE KEY UPDATE vote_count = vote_count + 1
");

$stmt->bind_param("is", $spot_id, $vote_type);

if ($stmt->execute()) {
    $stmt->close();

    // Get updated vote counts for this spot
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
        $votes[] = $row;
    }

    $stmt->close();
    $conn->close();

    send_json([
        'success' => true,
        'message' => 'Vote recorded',
        'votes' => $votes
    ]);
} else {
    $stmt->close();
    $conn->close();

    send_json(['error' => 'Failed to record vote'], 500);
}
?>
