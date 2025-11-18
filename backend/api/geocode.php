<?php
/**
 * Geocoding Proxy Endpoint
 * 
 * Proxies requests to OpenStreetMap Nominatim API to avoid CORS issues.
 * Requires proper User-Agent and respects rate limits.
 * 
 * GET /api/geocode.php?q=new+caney,+texas&limit=1&email=contact@wherecanifish.com
 */

require_once __DIR__ . '/config.php';
set_cors_headers();

// Only allow GET requests
if ($_SERVER['REQUEST_METHOD'] !== 'GET') {
    send_json(['error' => 'Method not allowed'], 405);
}

// Get query parameters
$query = $_GET['q'] ?? '';
$email = $_GET['email'] ?? 'contact@wherecanifish.com';
$limit = isset($_GET['limit']) ? (int)$_GET['limit'] : 1;

if (empty($query)) {
    send_json(['error' => 'Query parameter "q" is required'], 400);
}

// Validate limit
if ($limit < 1 || $limit > 10) {
    $limit = 1; // Default to 1 if invalid
}

// Build Nominatim API URL
$nominatimUrl = sprintf(
    'https://nominatim.openstreetmap.org/search?q=%s&format=json&limit=%d&email=%s',
    urlencode($query),
    $limit,
    urlencode($email)
);

// Make request with proper User-Agent (required by Nominatim)
$ch = curl_init($nominatimUrl);
curl_setopt_array($ch, [
    CURLOPT_RETURNTRANSFER => true,
    CURLOPT_USERAGENT => 'WhereCanIFish.com/1.0 (contact@wherecanifish.com)', // Required by Nominatim
    CURLOPT_HTTPHEADER => [
        'Accept: application/json',
    ],
    CURLOPT_TIMEOUT => 10,
    CURLOPT_FOLLOWLOCATION => true,
]);

$response = curl_exec($ch);
$httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
$error = curl_error($ch);
curl_close($ch);

if ($error) {
    error_log("Geocoding error: $error");
    send_json(['error' => 'Geocoding service unavailable'], 503);
}

if ($httpCode !== 200) {
    error_log("Nominatim API returned HTTP $httpCode for query: $query");
    send_json(['error' => 'Geocoding service error'], $httpCode);
}

$data = json_decode($response, true);
if (json_last_error() !== JSON_ERROR_NONE) {
    error_log("Invalid JSON response from Nominatim: " . json_last_error_msg());
    send_json(['error' => 'Invalid response from geocoding service'], 500);
}

// Return the data as-is (Nominatim returns an array of results)
send_json($data);
?>

