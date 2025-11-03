<?php
/**
 * Production Database Configuration for Hostinger
 *
 * INSTRUCTIONS:
 * 1. Get your database credentials from Hostinger cPanel
 * 2. Update the DB_* constants below with your actual values
 * 3. Rename this file to config.php when deploying
 */

// ========================================
// HOSTINGER DATABASE CREDENTIALS
// ========================================
// TODO: Update these with your Hostinger database credentials from cPanel
define('DB_HOST', 'localhost');  // Usually 'localhost' on Hostinger
define('DB_USER', 'YOUR_DB_USERNAME');  // From Hostinger MySQL Databases
define('DB_PASS', 'YOUR_DB_PASSWORD');  // From Hostinger MySQL Databases
define('DB_NAME', 'YOUR_DB_NAME');      // From Hostinger MySQL Databases

// ========================================
// CORS SETTINGS
// ========================================
$allowed_origins = [
    'https://wherecanifish.com',
    'https://www.wherecanifish.com'
];

// ========================================
// RATE LIMITING
// ========================================
define('RATE_LIMIT_SUBMISSIONS', 3);  // Max submissions per hour per IP
define('RATE_LIMIT_VOTES', 10);       // Max votes per hour per IP

/**
 * Get database connection
 *
 * @return mysqli Database connection
 */
function get_db_connection() {
    $conn = new mysqli(DB_HOST, DB_USER, DB_PASS, DB_NAME);

    if ($conn->connect_error) {
        error_log("Database connection failed: " . $conn->connect_error);
        http_response_code(500);
        die(json_encode(['error' => 'Database connection failed']));
    }

    $conn->set_charset('utf8mb4');
    return $conn;
}

/**
 * Set CORS headers
 */
function set_cors_headers() {
    global $allowed_origins;

    $origin = isset($_SERVER['HTTP_ORIGIN']) ? $_SERVER['HTTP_ORIGIN'] : '';

    if (in_array($origin, $allowed_origins)) {
        header('Access-Control-Allow-Origin: ' . $origin);
    }

    header('Access-Control-Allow-Methods: GET, POST, OPTIONS');
    header('Access-Control-Allow-Headers: Content-Type');
    header('Access-Control-Max-Age: 86400');

    // Handle preflight requests
    if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
        http_response_code(200);
        exit;
    }
}

/**
 * Get hashed IP for rate limiting (privacy-conscious)
 *
 * @return string SHA-256 hash of IP address
 */
function get_ip_hash() {
    $ip = $_SERVER['REMOTE_ADDR'] ?? 'unknown';
    return hash('sha256', $ip . date('Y-m-d H'));  // Hour-based salt
}

/**
 * Send JSON response
 *
 * @param mixed $data Data to encode
 * @param int $status HTTP status code
 */
function send_json($data, $status = 200) {
    http_response_code($status);
    header('Content-Type: application/json');
    echo json_encode($data);
    exit;
}
?>
