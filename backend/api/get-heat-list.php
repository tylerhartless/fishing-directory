<?php
/**
 * API Endpoint: Get Heat List for a fishing spot
 *
 * GET /api/get-heat-list.php?canonical_id=tx-anderson-trinity-river-anderson001
 *
 * Returns species that have been logged at this canonical, ranked by
 * time-decayed catch score. Empty array when no reports exist yet.
 *
 * Tier thresholds:
 *   common:   score >= TIER_THRESHOLD_COMMON
 *   uncommon: score >= TIER_THRESHOLD_UNCOMMON
 *   rare:     score > 0
 *   (unreported species are not returned — modal sources them separately)
 */

define('TIER_THRESHOLD_COMMON', 50);
define('TIER_THRESHOLD_UNCOMMON', 20);

require_once 'config.php';

set_cors_headers();
header('Content-Type: application/json');

if ($_SERVER['REQUEST_METHOD'] !== 'GET') {
    send_json(['error' => 'Method not allowed'], 405);
}

$canonical_id = trim($_GET['canonical_id'] ?? '');
if ($canonical_id === '' || strlen($canonical_id) > 64 || !preg_match('/^[a-z0-9-]+$/', $canonical_id)) {
    send_json(['error' => 'Invalid canonical_id'], 400);
}

$conn = get_db_connection();

$stmt = $conn->prepare("
    SELECT
        ms.id,
        ms.common_name,
        ms.icon,
        ms.priority_order,
        SUM(cr.current_score) AS total_score,
        COUNT(cr.id) AS report_count
    FROM catch_reports cr
    JOIN master_species ms ON cr.master_species_id = ms.id
    WHERE cr.canonical_id = ?
    GROUP BY ms.id, ms.common_name, ms.icon, ms.priority_order
    ORDER BY total_score DESC, ms.priority_order ASC
");

$stmt->bind_param('s', $canonical_id);
$stmt->execute();
$result = $stmt->get_result();

$species = [];
while ($row = $result->fetch_assoc()) {
    $total_score = floatval($row['total_score']);
    if ($total_score >= TIER_THRESHOLD_COMMON) {
        $tier = 'common';
    } elseif ($total_score >= TIER_THRESHOLD_UNCOMMON) {
        $tier = 'uncommon';
    } else {
        $tier = 'rare';
    }

    $species[] = [
        'id' => intval($row['id']),
        'common_name' => $row['common_name'],
        'icon' => $row['icon'],
        'priority_order' => intval($row['priority_order']),
        'total_score' => $total_score,
        'report_count' => intval($row['report_count']),
        'tier' => $tier,
        'has_reports' => true,
    ];
}

$stmt->close();
$conn->close();

send_json([
    'success' => true,
    'canonical_id' => $canonical_id,
    'species' => $species,
]);
