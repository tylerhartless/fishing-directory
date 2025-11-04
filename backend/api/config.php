<?php
/**
 * LOCAL DEVELOPMENT (DOCKER) CONFIGURATION
 *
 * This file contains credentials for your local Docker environment.
 * It is IGNORED by Git and should NOT be on your production server.
 */

// ========================================
// DOCKER DATABASE CREDENTIALS
// ========================================
define('DB_HOST', 'mysql');  // Docker service name
define('DB_USER', 'fishing_user');
define('DB_PASS', 'fishing_password');
define('DB_NAME', 'fishing_directory');

// ========================================
// CORS SETTINGS
// ========================================
$allowed_origins = [
    'http://localhost:4321',  // Astro dev server
    'http://localhost:3000',  // Alternative dev port
    'http://localhost:8000',  // PHP server
    'http://100.79.50.67:4321',  // Tailscale access
];

// ========================================
// RATE LIMITING
// ========================================
define('RATE_LIMIT_SUBMISSIONS', 3);
define('RATE_LIMIT_VOTES', 10);

/*
 * Maintenance mode logic
 * (Copied from your original config.php)
 */
function is_whitelisted_ip($ip, $whitelistPaths) {
    if (!$ip) return false;
    foreach ($whitelistPaths as $p) {
        if (!file_exists($p)) continue;
        $lines = preg_split('/\r?\n/', file_get_contents($p));
        foreach ($lines as $line) {
            $line = trim($line);
            if ($line === '' || strpos($line, '#') === 0) continue;
            if ($line === $ip) return true;
        }
    }
    if (php_sapi_name() === 'cli' || in_array($ip, ['127.0.0.1', '::1'])) return true;
    return false;
}

$candidates = [
    __DIR__ . '/../MAINTENANCE',
    __DIR__ . '/../../deploy/public_html/MAINTENANCE',
];
if (!empty($_SERVER['DOCUMENT_ROOT'])) {
    $candidates[] = rtrim($_SERVER['DOCUMENT_ROOT'], "\\/") . '/MAINTENANCE';
}

$maintenance_on = false;
foreach ($candidates as $c) {
    if (file_exists($c)) { $maintenance_on = true; break; }
}

if ($maintenance_on) {
    $remote_ip = $_SERVER['REMOTE_ADDR'] ?? '';
    $whitelistPaths = [
        __DIR__ . '/../MAINTENANCE_WHITELIST',
        __DIR__ . '/../../deploy/public_html/MAINTENANCE_WHITELIST'
    ];
    if (!empty($_SERVER['DOCUMENT_ROOT'])) {
        $whitelistPaths[] = rtrim($_SERVER['DOCUMENT_ROOT'], "\\/") . '/MAINTENANCE_WHITELIST';
    }

    if (!is_whitelisted_ip($remote_ip, $whitelistPaths)) {
        $accept = $_SERVER['HTTP_ACCEPT'] ?? '';
        $request_uri = $_SERVER['REQUEST_URI'] ?? '';
        if (strpos($request_uri, '/api/') === 0 || strpos($accept, 'application/json') !== false) {
            http_response_code(503);
            header('Content-Type: application/json');
            echo json_encode(['error' => 'Site is temporarily down for maintenance. Please try again later.']);
            exit;
        }

        $htmlCandidates = [
            __DIR__ . '/../../deploy/public_html/maintenance.html',
            __DIR__ . '/../maintenance.html',
        ];
        if (!empty($_SERVER['DOCUMENT_ROOT'])) {
            $htmlCandidates[] = rtrim($_SERVER['DOCUMENT_ROOT'], "\\/") . '/maintenance.html';
        }

        foreach ($htmlCandidates as $h) {
            if (file_exists($h)) {
                http_response_code(503);
                header('Content-Type: text/html');
                echo file_get_contents($h);
                exit;
            }
        }

        http_response_code(503);
        header('Content-Type: text/plain');
        echo 'Site is temporarily down for maintenance. Please try again later.';
        exit;
    }
}

// ========================================
// HELPER FUNCTIONS
// ========================================

/**
 * Get database connection
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
    if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
        http_response_code(200);
        exit;
    }
}

/**
 * Get hashed IP for rate limiting
 */
function get_ip_hash() {
    $ip = $_SERVER['REMOTE_ADDR'] ?? 'unknown';
    return hash('sha256', $ip . date('Y-m-d H'));
}

/**
 * Send JSON response
 */
function send_json($data, $status = 200) {
    http_response_code($status);
    header('Content-Type: application/json');
    echo json_encode($data);
    exit;
}
?>
