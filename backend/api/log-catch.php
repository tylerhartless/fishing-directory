<?php
/**
 * API Endpoint: Log a catch (Species Prevalence System)
 *
 * POST /api/log-catch.php
 *
 * Body (JSON):
 * {
 *   "spot_id": 123,
 *   "species_id": 5,
 *   "catch_date": "2025-11-12"
 * }
 *
 * Response:
 * {
 *   "success": true,
 *   "message": "Catch logged successfully",
 *   "report_id": 456
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
$species_id = filter_var($input['species_id'] ?? null, FILTER_VALIDATE_INT);
$catch_date = trim($input['catch_date'] ?? '');

if (!$spot_id) {
    send_json(['error' => 'Invalid spot_id'], 400);
}

if (!$species_id) {
    send_json(['error' => 'Invalid species_id'], 400);
}

// Validate date format (YYYY-MM-DD)
if (!preg_match('/^\d{4}-\d{2}-\d{2}$/', $catch_date)) {
    send_json(['error' => 'Invalid catch_date format (use YYYY-MM-DD)'], 400);
}

// Validate date is not in the future
$catch_timestamp = strtotime($catch_date);
if ($catch_timestamp > time()) {
    send_json(['error' => 'Catch date cannot be in the future'], 400);
}

// Validate date is not too old (e.g., within last 30 days)
$thirty_days_ago = strtotime('-30 days');
if ($catch_timestamp < $thirty_days_ago) {
    send_json(['error' => 'Catch date must be within the last 30 days'], 400);
}

// Rate limiting: 5 catch reports per hour per IP (disabled in local dev)
$conn = get_db_connection();

// Always hash IP for database storage (privacy-preserving)
$ip_hash = hash('sha256', $_SERVER['REMOTE_ADDR'] ?? 'unknown');

// Check rate limit only in production
if (!is_local_dev()) {
$stmt = $conn->prepare("
    SELECT COUNT(*) as count
    FROM catch_reports
    WHERE user_ip_hash = ?
      AND created_at > DATE_SUB(NOW(), INTERVAL 1 HOUR)
");

if (!$stmt) {
    error_log('log-catch: Failed to prepare rate limit query: ' . $conn->error);
    $conn->close();
    send_json(['error' => 'Server error while checking rate limits'], 500);
}

$stmt->bind_param("s", $ip_hash);
    $stmt->execute();
    $result = $stmt->get_result();
    $row = $result->fetch_assoc();
    $stmt->close();
    
    if ($row['count'] >= 5) {
        $conn->close();
        send_json(['error' => 'Rate limit exceeded. Max 5 catches per hour.'], 429);
    }
}

// Verify spot exists
$stmt = $conn->prepare("SELECT id FROM fishing_spots WHERE id = ?");
if (!$stmt) {
    error_log('log-catch: Failed to prepare fishing spot lookup: ' . $conn->error);
    $conn->close();
    send_json(['error' => 'Server error while verifying spot'], 500);
}
$stmt->bind_param("i", $spot_id);
$stmt->execute();
$result = $stmt->get_result();

if ($result->num_rows === 0) {
    $stmt->close();
    $conn->close();
    send_json(['error' => 'Fishing spot not found'], 404);
}

$stmt->close();

// Verify species is in the spot's potential_species list
$stmt = $conn->prepare("
    SELECT ps.id
    FROM potential_species ps
    WHERE ps.fishing_spot_id = ?
      AND ps.master_species_id = ?
");

if (!$stmt) {
    error_log('log-catch: Failed to prepare potential species lookup: ' . $conn->error);
    $conn->close();
    send_json(['error' => 'Server error while verifying species'], 500);
}

$stmt->bind_param("ii", $spot_id, $species_id);
$stmt->execute();
$result = $stmt->get_result();

if ($result->num_rows === 0) {
    $stmt->close();
    $conn->close();
    send_json(['error' => 'Species not available for this fishing spot'], 400);
}

$stmt->close();

// Insert catch report with default base_score of 10
$base_score = 10.00;

$stmt = $conn->prepare("
    INSERT INTO catch_reports
    (fishing_spot_id, master_species_id, user_ip_hash, catch_date, base_score, current_score, last_decay_date)
    VALUES (?, ?, ?, ?, ?, ?, ?)
");

if (!$stmt) {
    error_log('log-catch: Failed to prepare catch insert: ' . $conn->error);
    $conn->close();
    send_json(['error' => 'Server error while logging catch'], 500);
}

$stmt->bind_param(
    "iissdds",
    $spot_id,
    $species_id,
    $ip_hash,
    $catch_date,
    $base_score,
    $base_score,
    $catch_date
);

if ($stmt->execute()) {
    $report_id = $stmt->insert_id;
    $stmt->close();
    $conn->close();

    send_json([
        'success' => true,
        'message' => 'Catch logged successfully',
        'report_id' => $report_id
    ]);
} else {
    $error = $stmt->error;
    $stmt->close();
    $conn->close();

    error_log("Failed to log catch: " . $error);
    send_json(['error' => 'Failed to log catch'], 500);
}
?>
