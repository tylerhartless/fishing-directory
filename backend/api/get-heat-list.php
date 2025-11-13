<?php
/**
 * API Endpoint: Get Heat List for a fishing spot
 *
 * GET /api/get-heat-list.php?spot_id=123
 *
 * Returns:
 * {
 *   "success": true,
 *   "spot_id": 123,
 *   "species": [
 *     {
 *       "id": 5,
 *       "common_name": "Largemouth Bass",
 *       "icon": "🎣",
 *       "priority_order": 1,
 *       "total_score": 1850.50,
 *       "report_count": 12,
 *       "tier": "uncommon",
 *       "has_reports": true
 *     },
 *     {
 *       "id": 3,
 *       "common_name": "Bluegill",
 *       "icon": "🐟",
 *       "priority_order": 3,
 *       "total_score": 0,
 *       "report_count": 0,
 *       "tier": "unreported",
 *       "has_reports": false
 *     }
 *   ]
 * }
 *
 * Tier Thresholds (configurable - adjust for launch vs. mature system):
 * - common: score >= TIER_THRESHOLD_COMMON (default: 50 for launch, was 5000)
 * - uncommon: score >= TIER_THRESHOLD_UNCOMMON and < TIER_THRESHOLD_COMMON (default: 20 for launch, was 1000)
 * - rare: score > 0 and < TIER_THRESHOLD_UNCOMMON (default: < 20 for launch, was < 1000)
 * - unreported: score = 0
 */

// ========================================
// TIER THRESHOLD CONFIGURATION
// ========================================
// Adjust these values to tune the rarity system
// Each catch = 10 points, so thresholds are in multiples of 10
// For launch: Lower thresholds to show activity sooner
// For mature system: Increase thresholds as data accumulates
define('TIER_THRESHOLD_COMMON', 50);      // 5+ catches = Common (was 5000 = 500+ catches)
define('TIER_THRESHOLD_UNCOMMON', 20);   // 2+ catches = Uncommon (was 1000 = 100+ catches)
// Rare: 1 catch (10 points) = > 0 and < 20
// Unreported: 0 catches = 0 points

require_once 'config.php';

set_cors_headers();
header('Content-Type: application/json');

// Only accept GET requests
if ($_SERVER['REQUEST_METHOD'] !== 'GET') {
    send_json(['error' => 'Method not allowed'], 405);
}

// Validate spot_id
$spot_id = filter_var($_GET['spot_id'] ?? null, FILTER_VALIDATE_INT);

if (!$spot_id) {
    send_json(['error' => 'Invalid spot_id'], 400);
}

$conn = get_db_connection();

// Verify spot exists
$stmt = $conn->prepare("SELECT id FROM fishing_spots WHERE id = ?");
$stmt->bind_param("i", $spot_id);
$stmt->execute();
$result = $stmt->get_result();

if ($result->num_rows === 0) {
    $stmt->close();
    $conn->close();
    send_json(['error' => 'Fishing spot not found'], 404);
}

$stmt->close();

// Get all potential species for this spot with their scores
// This query returns ALL potential species, with scores for those that have reports
$stmt = $conn->prepare("
    SELECT
        ms.id,
        ms.common_name,
        ms.icon,
        ms.priority_order,
        COALESCE(SUM(cr.current_score), 0) as total_score,
        COUNT(cr.id) as report_count
    FROM potential_species ps
    JOIN master_species ms ON ps.master_species_id = ms.id
    LEFT JOIN catch_reports cr ON cr.master_species_id = ms.id
        AND cr.fishing_spot_id = ps.fishing_spot_id
    WHERE ps.fishing_spot_id = ?
    GROUP BY ms.id, ms.common_name, ms.icon, ms.priority_order
    ORDER BY
        CASE WHEN COALESCE(SUM(cr.current_score), 0) > 0 THEN 0 ELSE 1 END,
        COALESCE(SUM(cr.current_score), 0) DESC,
        ms.priority_order ASC
");

$stmt->bind_param("i", $spot_id);
$stmt->execute();
$result = $stmt->get_result();

$species = [];

while ($row = $result->fetch_assoc()) {
    $total_score = floatval($row['total_score']);
    $report_count = intval($row['report_count']);

    // Determine tier based on score (using configurable thresholds)
    if ($total_score >= TIER_THRESHOLD_COMMON) {
        $tier = 'common';
    } elseif ($total_score >= TIER_THRESHOLD_UNCOMMON) {
        $tier = 'uncommon';
    } elseif ($total_score > 0) {
        $tier = 'rare';
    } else {
        $tier = 'unreported';
    }

    $species[] = [
        'id' => intval($row['id']),
        'common_name' => $row['common_name'],
        'icon' => $row['icon'],
        'priority_order' => intval($row['priority_order']),
        'total_score' => $total_score,
        'report_count' => $report_count,
        'tier' => $tier,
        'has_reports' => $total_score > 0
    ];
}

$stmt->close();
$conn->close();

send_json([
    'success' => true,
    'spot_id' => $spot_id,
    'species' => $species
]);
?>
