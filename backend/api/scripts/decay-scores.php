#!/usr/bin/env php
<?php
/**
 * Time-Decay Scoring Script
 *
 * This script applies time-decay to all catch report scores.
 * Should be run daily via cron job.
 *
 * Decay Formula:
 * - Each week (7 days) since last decay, multiply score by 0.95 (5% decay per week)
 * - This prevents "gaming" the system and keeps rankings fresh
 *
 * Example decay:
 * - Day 0: 10.00 points
 * - Week 1: 9.50 points
 * - Week 2: 9.03 points
 * - Week 4: 8.15 points
 * - Week 12: 5.40 points
 * - Week 24: 2.92 points
 * - Week 52: 0.72 points
 *
 * Setup:
 * 1. Make executable: chmod +x decay-scores.php
 * 2. Add to crontab: 0 2 * * * /path/to/decay-scores.php >> /var/log/decay-scores.log 2>&1
 *    (Runs daily at 2:00 AM)
 *
 * Manual run:
 * php decay-scores.php
 */

// Change to script directory
chdir(__DIR__);

// Config is in parent directory when running in Docker container
// Try both paths for flexibility
if (file_exists(__DIR__ . '/../api/config.php')) {
    require_once __DIR__ . '/../api/config.php';
} elseif (file_exists(__DIR__ . '/../config.php')) {
    require_once __DIR__ . '/../config.php';
} else {
    die("Error: Could not find config.php\n");
}

$conn = get_db_connection();

echo "=== Species Prevalence Time-Decay Script ===\n";
echo "Started at: " . date('Y-m-d H:i:s') . "\n\n";

// Get all catch reports that need decay applied
$stmt = $conn->prepare("
    SELECT
        id,
        current_score,
        last_decay_date,
        DATEDIFF(CURDATE(), last_decay_date) as days_since_decay
    FROM catch_reports
    WHERE last_decay_date < CURDATE()
      AND current_score > 0.01
");

$stmt->execute();
$result = $stmt->get_result();

$reports_to_update = [];

while ($row = $result->fetch_assoc()) {
    $reports_to_update[] = $row;
}

$stmt->close();

if (empty($reports_to_update)) {
    echo "No reports need decay applied.\n";
    $conn->close();
    exit(0);
}

echo "Found " . count($reports_to_update) . " reports to decay.\n\n";

// Decay parameters
$decay_rate = 0.95;  // 5% decay per week
$days_per_period = 7; // Weekly decay

$updated_count = 0;
$deleted_count = 0;

// Update each report
foreach ($reports_to_update as $report) {
    $id = $report['id'];
    $current_score = floatval($report['current_score']);
    $days_since_decay = intval($report['days_since_decay']);

    // Calculate number of complete weeks since last decay
    $weeks_elapsed = floor($days_since_decay / $days_per_period);

    if ($weeks_elapsed < 1) {
        continue; // Skip if less than a week has passed
    }

    // Apply decay: score * (0.95 ^ weeks_elapsed)
    $new_score = $current_score * pow($decay_rate, $weeks_elapsed);

    // If score drops below 0.01, delete the report (essentially expired)
    if ($new_score < 0.01) {
        $stmt = $conn->prepare("DELETE FROM catch_reports WHERE id = ?");
        $stmt->bind_param("i", $id);
        $stmt->execute();
        $stmt->close();
        $deleted_count++;

        echo "Report ID $id: Score expired (was $current_score) - DELETED\n";
    } else {
        // Update the score and last_decay_date
        $stmt = $conn->prepare("
            UPDATE catch_reports
            SET current_score = ?,
                last_decay_date = CURDATE()
            WHERE id = ?
        ");

        $stmt->bind_param("di", $new_score, $id);
        $stmt->execute();
        $stmt->close();
        $updated_count++;

        echo "Report ID $id: $current_score → " . number_format($new_score, 2) . " (-" . number_format((1 - $new_score / $current_score) * 100, 1) . "%)\n";
    }
}

$conn->close();

echo "\n=== Decay Complete ===\n";
echo "Reports updated: $updated_count\n";
echo "Reports deleted: $deleted_count\n";
echo "Finished at: " . date('Y-m-d H:i:s') . "\n";

exit(0);
?>
