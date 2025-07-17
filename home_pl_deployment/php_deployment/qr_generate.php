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

// Only allow GET requests
if ($_SERVER['REQUEST_METHOD'] !== 'GET') {
    http_response_code(405);
    echo json_encode(['error' => 'Method not allowed']);
    exit;
}

// Get employee ID from query parameters
$employee_id = $_GET['employee_id'] ?? '';

if (!$employee_id) {
    http_response_code(400);
    echo json_encode(['error' => 'Employee ID required']);
    exit;
}

// Database connection
try {
    $pdo = new PDO("sqlite:timetracker_pro.db");
    $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
    
    // Find employee
    $stmt = $pdo->prepare("SELECT * FROM employees WHERE id = ?");
    $stmt->execute([$employee_id]);
    $employee = $stmt->fetch(PDO::FETCH_ASSOC);
    
    if (!$employee) {
        http_response_code(404);
        echo json_encode(['error' => 'Employee not found']);
        exit;
    }
    
    // Simple QR code data structure
    $qr_data = [
        'employee_id' => $employee['id'],
        'employee_name' => $employee['name'],
        'company_id' => $employee['company_id'],
        'qr_code' => $employee['qr_code'],
        'generated_at' => date('Y-m-d H:i:s')
    ];
    
    // For production, you would generate actual QR code image
    // For now, return QR code data that can be used to generate QR on frontend
    $response = [
        'qr_code' => $employee['qr_code'],
        'employee_name' => $employee['name'],
        'employee_id' => $employee['id'],
        'company_id' => $employee['company_id'],
        'qr_data' => json_encode($qr_data),
        'qr_url' => 'https://timetrackerpro.pl/qr_scan.php',
        'message' => 'QR code generated successfully'
    ];
    
    echo json_encode($response);
    
} catch (Exception $e) {
    http_response_code(500);
    echo json_encode(['error' => 'Internal server error: ' . $e->getMessage()]);
}
?>