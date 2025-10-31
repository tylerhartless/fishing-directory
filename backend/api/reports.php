<?php
/**
 * API Endpoint: Get fishing reports for a specific spot
 *
 * GET /api/reports.php?spot_id=123
 *
 * Returns approved fishing reports in JSON format
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

// Prepare query to get approved reports
$stmt = $conn->prepare("
    SELECT
        fish_species,
        catch_count,
        DATE_FORMAT(report_date, '%Y-%m-%d') as report_date,
        notes,
        DATE_FORMAT(created_at, '%Y-%m-%d') as submitted_date
    FROM fishing_reports
    WHERE fishing_spot_id = ? AND is_approved = 1
    ORDER BY report_date DESC
    LIMIT 20
");

$stmt->bind_param("i", $spot_id);
$stmt->execute();
$result = $stmt->get_result();

$reports = [];
while ($row = $result->fetch_assoc()) {
    $reports[] = $row;
}

$stmt->close();
$conn->close();

// Return results
send_json([
    'success' => true,
    'count' => count($reports),
    'reports' => $reports
]);
?>
