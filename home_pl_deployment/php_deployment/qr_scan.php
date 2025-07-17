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

// Only allow POST requests
if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405);
    echo json_encode(['error' => 'Method not allowed']);
    exit;
}

// Get request body
$json = file_get_contents('php://input');
$data = json_decode($json, true);

if (!$data || !$data['qr_code']) {
    http_response_code(400);
    echo json_encode(['error' => 'QR code required']);
    exit;
}

$qr_code = $data['qr_code'];

// Database connection
try {
    $pdo = new PDO("sqlite:timetracker_pro.db");
    $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
    
    // Find employee by QR code
    $stmt = $pdo->prepare("SELECT * FROM employees WHERE qr_code = ?");
    $stmt->execute([$qr_code]);
    $employee = $stmt->fetch(PDO::FETCH_ASSOC);
    
    if (!$employee) {
        http_response_code(404);
        echo json_encode(['error' => 'Employee not found']);
        exit;
    }
    
    // Check last entry to determine entry type
    $stmt = $pdo->prepare("
        SELECT entry_type FROM time_entries 
        WHERE employee_id = ? 
        ORDER BY timestamp DESC 
        LIMIT 1
    ");
    $stmt->execute([$employee['id']]);
    $last_entry = $stmt->fetch(PDO::FETCH_ASSOC);
    
    $entry_type = 'check_in';
    if ($last_entry && $last_entry['entry_type'] === 'check_in') {
        $entry_type = 'check_out';
    }
    
    // Insert time entry
    $entry_id = 'time-' . uniqid();
    $stmt = $pdo->prepare("
        INSERT INTO time_entries (id, employee_id, company_id, entry_type, timestamp)
        VALUES (?, ?, ?, ?, ?)
    ");
    
    $stmt->execute([
        $entry_id,
        $employee['id'],
        $employee['company_id'],
        $entry_type,
        date('Y-m-d H:i:s')
    ]);
    
    $response = [
        'id' => $entry_id,
        'employee_id' => $employee['id'],
        'employee_name' => $employee['name'],
        'company_id' => $employee['company_id'],
        'entry_type' => $entry_type,
        'timestamp' => date('Y-m-d H:i:s'),
        'message' => $entry_type === 'check_in' ? 'Wejście zarejestrowane' : 'Wyjście zarejestrowane'
    ];
    
    http_response_code(201);
    echo json_encode($response);
    
} catch (Exception $e) {
    http_response_code(500);
    echo json_encode(['error' => 'Internal server error: ' . $e->getMessage()]);
}
?>