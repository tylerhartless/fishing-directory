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
    'https://wherecanifish.com',  // Your production domain
    'https://www.wherecanifish.com'
];

/*
 * Maintenance mode
 * If a file named "MAINTENANCE" exists in one of the candidate locations, the site will return
 * a 503 and show the maintenance page for non-whitelisted IPs. This works for both API and
 * browser requests. To whitelist IPs create a file named MAINTENANCE_WHITELIST with one IP
 * per line (or use Hostinger control panel to allow your IP).
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
            // support CIDR? not implemented — exact-match only for safety
        }
    }
    // locally allow CLI and loopback
    if (php_sapi_name() === 'cli' || in_array($ip, ['127.0.0.1', '::1'])) return true;
    return false;
}

// candidate maintenance flag locations (relative and server DOCUMENT_ROOT)
$candidates = [
    __DIR__ . '/../MAINTENANCE',                        // backend/MAINTENANCE
    __DIR__ . '/../../deploy/public_html/MAINTENANCE',  // deploy/public_html/MAINTENANCE
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
    // whitelist file candidates (same search locations)
    $whitelistPaths = [
        __DIR__ . '/../MAINTENANCE_WHITELIST',
        __DIR__ . '/../../deploy/public_html/MAINTENANCE_WHITELIST'
    ];
    if (!empty($_SERVER['DOCUMENT_ROOT'])) {
        $whitelistPaths[] = rtrim($_SERVER['DOCUMENT_ROOT'], "\\/") . '/MAINTENANCE_WHITELIST';
    }

    if (!is_whitelisted_ip($remote_ip, $whitelistPaths)) {
        // If it's an API/JSON request, return JSON 503
        $accept = $_SERVER['HTTP_ACCEPT'] ?? '';
        $request_uri = $_SERVER['REQUEST_URI'] ?? '';
        if (strpos($request_uri, '/api/') === 0 || strpos($accept, 'application/json') !== false) {
            http_response_code(503);
            header('Content-Type: application/json');
            echo json_encode(['error' => 'Site is temporarily down for maintenance. Please try again later.']);
            exit;
        }

        // Otherwise serve the maintenance HTML if available
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

        // Fallback plain text
        http_response_code(503);
        header('Content-Type: text/plain');
        echo 'Site is temporarily down for maintenance. Please try again later.';
        exit;
    }
}

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
