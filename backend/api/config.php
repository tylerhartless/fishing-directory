<?php
/**
 * Database configuration for API
 *
 * IMPORTANT: Update these values with your Hostinger credentials
 * Keep this file secure and never commit to public repositories
 */

// Database connection settings
// Use Docker settings for local development, Hostinger settings for production
define('DB_HOST', getenv('DB_HOST') ?: 'mysql');
define('DB_USER', getenv('DB_USER') ?: 'fishing_user');
define('DB_PASS', getenv('DB_PASS') ?: 'fishing_password');
define('DB_NAME', getenv('DB_NAME') ?: 'fishing_directory');

// CORS settings - update with your frontend domain
$allowed_origins = [
    'http://localhost:4321',  // Astro dev server
    'http://100.79.50.67:4321',  // Tailscale access
    'https://yourdomain.com',  // Your production domain
    'https://www.yourdomain.com'
];

// Rate limiting settings
define('RATE_LIMIT_SUBMISSIONS', 3);  // Max submissions per hour
define('RATE_LIMIT_VOTES', 10);       // Max votes per hour

/**
 * Get database connection
 *
 * @return mysqli Database connection
 */
function get_db_connection() {
    $conn = new mysqli(DB_HOST, DB_USER, DB_PASS, DB_NAME);

    if ($conn->connect_error) {
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
