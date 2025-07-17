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
        // Get users
        if ($current_user['type'] === 'owner') {
            $stmt = $pdo->query("SELECT id, username, type, role, company_id, company_name, created_at FROM users ORDER BY created_at DESC");
        } elseif ($current_user['type'] === 'admin') {
            $stmt = $pdo->prepare("SELECT id, username, type, role, company_id, company_name, created_at FROM users WHERE company_id = ? ORDER BY created_at DESC");
            $stmt->execute([$current_user['company_id']]);
        } else {
            http_response_code(403);
            echo json_encode(['error' => 'Access denied']);
            exit;
        }
        
        $users = $stmt->fetchAll(PDO::FETCH_ASSOC);
        echo json_encode($users);
        
    } elseif ($_SERVER['REQUEST_METHOD'] === 'POST') {
        // Add user
        if ($current_user['type'] === 'user') {
            http_response_code(403);
            echo json_encode(['error' => 'Access denied']);
            exit;
        }
        
        $json = file_get_contents('php://input');
        $data = json_decode($json, true);
        
        if (!$data || !$data['username'] || !$data['password']) {
            http_response_code(400);
            echo json_encode(['error' => 'Username and password required']);
            exit;
        }
        
        $user_id = 'user-' . uniqid();
        
        $stmt = $pdo->prepare("
            INSERT INTO users (id, username, password_hash, type, role, company_id, company_name)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ");
        
        $stmt->execute([
            $user_id,
            $data['username'],
            password_hash($data['password'], PASSWORD_DEFAULT),
            $data['type'] ?? 'user',
            $data['role'] ?? 'user',
            $current_user['type'] === 'owner' ? ($data['company_id'] ?? null) : $current_user['company_id'],
            $data['company_name'] ?? $current_user['company_name']
        ]);
        
        $user = [
            'id' => $user_id,
            'username' => $data['username'],
            'type' => $data['type'] ?? 'user',
            'role' => $data['role'] ?? 'user',
            'company_id' => $current_user['type'] === 'owner' ? ($data['company_id'] ?? null) : $current_user['company_id'],
            'company_name' => $data['company_name'] ?? $current_user['company_name'],
            'created_at' => date('Y-m-d H:i:s')
        ];
        
        http_response_code(201);
        echo json_encode($user);
        
    } else {
        http_response_code(405);
        echo json_encode(['error' => 'Method not allowed']);
    }
    
} catch (Exception $e) {
    http_response_code(500);
    echo json_encode(['error' => 'Internal server error: ' . $e->getMessage()]);
}
?>