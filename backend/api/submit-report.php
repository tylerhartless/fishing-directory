<?php
/**
 * API Endpoint: Submit a fishing report
 *
 * POST /api/submit-report.php
 *
 * Body (JSON):
 * {
 *   "spot_id": 123,
 *   "fish_species": "Largemouth Bass",
 *   "catch_count": 3,
 *   "report_date": "2025-10-30",
 *   "notes": "Great morning, caught on crankbaits"
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

// Validate required fields
$spot_id = filter_var($input['spot_id'] ?? null, FILTER_VALIDATE_INT);
$fish_species = trim($input['fish_species'] ?? '');
$catch_count = filter_var($input['catch_count'] ?? 1, FILTER_VALIDATE_INT);
$report_date = $input['report_date'] ?? date('Y-m-d');
$notes = trim($input['notes'] ?? '');

// Validation
if (!$spot_id) {
    send_json(['error' => 'Invalid spot_id'], 400);
}

if (empty($fish_species) || strlen($fish_species) > 100) {
    send_json(['error' => 'Invalid fish species'], 400);
}

if ($catch_count < 0 || $catch_count > 1000) {
    send_json(['error' => 'Invalid catch count'], 400);
}

if (strlen($notes) > 500) {
    send_json(['error' => 'Notes too long (max 500 characters)'], 400);
}

$conn = get_db_connection();

// Check rate limiting (max 3 submissions per hour) - disabled in local dev
if (!is_local_dev()) {
    $ip_hash = get_ip_hash();
    
    $stmt = $conn->prepare("
        SELECT COUNT(*) as count
        FROM fishing_reports
        WHERE user_ip_hash = ?
        AND created_at > DATE_SUB(NOW(), INTERVAL 1 HOUR)
    ");
    
    $stmt->bind_param("s", $ip_hash);
    $stmt->execute();
    $result = $stmt->get_result()->fetch_assoc();
    $stmt->close();
    
    if ($result['count'] >= RATE_LIMIT_SUBMISSIONS) {
        $conn->close();
        send_json([
            'error' => 'Too many submissions. Please wait before submitting again.',
            'retry_after' => 3600
        ], 429);
    }
}

// Insert fishing report (pending approval)
$stmt = $conn->prepare("
    INSERT INTO fishing_reports
    (fishing_spot_id, user_ip_hash, fish_species, catch_count, report_date, notes, is_approved)
    VALUES (?, ?, ?, ?, ?, ?, 0)
");

$stmt->bind_param("ississ", $spot_id, $ip_hash, $fish_species, $catch_count, $report_date, $notes);

if ($stmt->execute()) {
    $report_id = $stmt->insert_id;
    $stmt->close();
    $conn->close();

    send_json([
        'success' => true,
        'message' => 'Fishing report submitted successfully! It will appear after review.',
        'report_id' => $report_id
    ], 201);
} else {
    $stmt->close();
    $conn->close();

    send_json(['error' => 'Failed to submit report'], 500);
}
?>
