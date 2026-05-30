<?php
/**
 * API Endpoint: Log a catch (Species Prevalence System)
 *
 * POST /api/log-catch.php
 *
 * Body (JSON):
 * {
 *   "canonical_id": "tx-anderson-trinity-river-anderson001",
 *   "species_id": 5,
 *   "catch_date": "2026-05-12"
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

if (!function_exists('is_local_dev')) {
    function is_local_dev(): bool {
        return false;
    }
}

set_cors_headers();
header('Content-Type: application/json');

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    send_json(['error' => 'Method not allowed'], 405);
}

$input = json_decode(file_get_contents('php://input'), true);
if (!$input) {
    send_json(['error' => 'Invalid JSON'], 400);
}

$canonical_id = trim($input['canonical_id'] ?? '');
$species_id = filter_var($input['species_id'] ?? null, FILTER_VALIDATE_INT);
$catch_date = trim($input['catch_date'] ?? '');

if ($canonical_id === '' || strlen($canonical_id) > 64 || !preg_match('/^[a-z0-9-]+$/', $canonical_id)) {
    send_json(['error' => 'Invalid canonical_id'], 400);
}

if (!$species_id) {
    send_json(['error' => 'Invalid species_id'], 400);
}

if (!preg_match('/^\d{4}-\d{2}-\d{2}$/', $catch_date)) {
    send_json(['error' => 'Invalid catch_date format (use YYYY-MM-DD)'], 400);
}

$catch_timestamp = strtotime($catch_date);
if ($catch_timestamp > time()) {
    send_json(['error' => 'Catch date cannot be in the future'], 400);
}

$thirty_days_ago = strtotime('-30 days');
if ($catch_timestamp < $thirty_days_ago) {
    send_json(['error' => 'Catch date must be within the last 30 days'], 400);
}

$conn = get_db_connection();
$ip_hash = hash('sha256', $_SERVER['REMOTE_ADDR'] ?? 'unknown');

// Rate limit (5 reports / hour / IP) — bypassed in local dev
if (!is_local_dev()) {
    $stmt = $conn->prepare("
        SELECT COUNT(*) AS count
        FROM catch_reports
        WHERE user_ip_hash = ?
          AND created_at > DATE_SUB(NOW(), INTERVAL 1 HOUR)
    ");
    if (!$stmt) {
        error_log('log-catch: prepare rate limit failed: ' . $conn->error);
        $conn->close();
        send_json(['error' => 'Server error while checking rate limits'], 500);
    }
    $stmt->bind_param('s', $ip_hash);
    $stmt->execute();
    $row = $stmt->get_result()->fetch_assoc();
    $stmt->close();

    if ($row['count'] >= 5) {
        $conn->close();
        send_json(['error' => 'Rate limit exceeded. Max 5 catches per hour.'], 429);
    }
}

// Verify the species exists in master_species (no per-spot vocabulary anymore;
// any species in the controlled vocab is allowed at any canonical).
$stmt = $conn->prepare('SELECT id FROM master_species WHERE id = ?');
if (!$stmt) {
    error_log('log-catch: prepare species lookup failed: ' . $conn->error);
    $conn->close();
    send_json(['error' => 'Server error while verifying species'], 500);
}
$stmt->bind_param('i', $species_id);
$stmt->execute();
if ($stmt->get_result()->num_rows === 0) {
    $stmt->close();
    $conn->close();
    send_json(['error' => 'Species not recognized'], 400);
}
$stmt->close();

$base_score = 10.00;

$stmt = $conn->prepare("
    INSERT INTO catch_reports
        (canonical_id, master_species_id, user_ip_hash, catch_date, base_score, current_score, last_decay_date)
    VALUES (?, ?, ?, ?, ?, ?, ?)
");
if (!$stmt) {
    error_log('log-catch: prepare catch insert failed: ' . $conn->error);
    $conn->close();
    send_json(['error' => 'Server error while logging catch'], 500);
}

$stmt->bind_param(
    'sissdds',
    $canonical_id,
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
        'report_id' => $report_id,
    ]);
} else {
    $error = $stmt->error;
    $stmt->close();
    $conn->close();
    error_log('Failed to log catch: ' . $error);
    send_json(['error' => 'Failed to log catch'], 500);
}
