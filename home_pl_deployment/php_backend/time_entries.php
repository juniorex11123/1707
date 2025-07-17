<?php
header('Content-Type: application/json');
header('Access-Control-Allow-Origin: https://timetrackerpro.pl');
header('Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type, Authorization');
header('Access-Control-Allow-Credentials: true');

// Handle CORS preflight
if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(200);
    exit;
}

// Simple JWT verification
function verify_jwt($token) {
    $parts = explode('.', $token);
    if (count($parts) !== 3) {
        return false;
    }
    
    $header = $parts[0];
    $payload = $parts[1];
    $signature = $parts[2];
    
    $expectedSignature = hash_hmac('sha256', $header . '.' . $payload, 'your-secret-key', true);
    $expectedSignatureEncoded = rtrim(strtr(base64_encode($expectedSignature), '+/', '-_'), '=');
    
    if ($signature !== $expectedSignatureEncoded) {
        return false;
    }
    
    $payloadData = json_decode(base64_decode(strtr($payload, '-_', '+/')), true);
    
    if ($payloadData['exp'] < time()) {
        return false;
    }
    
    return $payloadData;
}

// Get auth token
$auth_header = $_SERVER['HTTP_AUTHORIZATION'] ?? '';
if (!$auth_header || !str_starts_with($auth_header, 'Bearer ')) {
    http_response_code(401);
    echo json_encode(['error' => 'Authorization required']);
    exit;
}

$token = substr($auth_header, 7);
$user_data = verify_jwt($token);

if (!$user_data) {
    http_response_code(401);
    echo json_encode(['error' => 'Invalid token']);
    exit;
}

// Database connection
try {
    $pdo = new PDO("sqlite:timetracker_pro.db");
    $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
    
    // Get current user
    $stmt = $pdo->prepare("SELECT * FROM users WHERE id = ?");
    $stmt->execute([$user_data['user_id']]);
    $current_user = $stmt->fetch(PDO::FETCH_ASSOC);
    
    if (!$current_user) {
        http_response_code(401);
        echo json_encode(['error' => 'User not found']);
        exit;
    }
    
    if ($_SERVER['REQUEST_METHOD'] === 'GET') {
        // Get time entries
        $query = "
            SELECT te.*, e.name as employee_name 
            FROM time_entries te
            JOIN employees e ON te.employee_id = e.id
        ";
        
        if ($current_user['type'] === 'owner') {
            $query .= " ORDER BY te.timestamp DESC";
            $stmt = $pdo->query($query);
        } else {
            $query .= " WHERE te.company_id = ? ORDER BY te.timestamp DESC";
            $stmt = $pdo->prepare($query);
            $stmt->execute([$current_user['company_id']]);
        }
        
        $time_entries = $stmt->fetchAll(PDO::FETCH_ASSOC);
        echo json_encode($time_entries);
        
    } else {
        http_response_code(405);
        echo json_encode(['error' => 'Method not allowed']);
    }
    
} catch (Exception $e) {
    http_response_code(500);
    echo json_encode(['error' => 'Internal server error: ' . $e->getMessage()]);
}
?>