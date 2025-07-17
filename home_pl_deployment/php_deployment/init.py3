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

// Database initialization
function init_database() {
    $db_path = 'timetracker_pro.db';
    
    try {
        $pdo = new PDO("sqlite:$db_path");
        $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
        
        // Create tables
        $pdo->exec("
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                type TEXT NOT NULL,
                role TEXT NOT NULL,
                company_id TEXT,
                company_name TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ");
        
        $pdo->exec("
            CREATE TABLE IF NOT EXISTS companies (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ");
        
        $pdo->exec("
            CREATE TABLE IF NOT EXISTS employees (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT,
                phone TEXT,
                company_id TEXT NOT NULL,
                qr_code TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (company_id) REFERENCES companies(id)
            )
        ");
        
        $pdo->exec("
            CREATE TABLE IF NOT EXISTS time_entries (
                id TEXT PRIMARY KEY,
                employee_id TEXT NOT NULL,
                company_id TEXT NOT NULL,
                entry_type TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (employee_id) REFERENCES employees(id),
                FOREIGN KEY (company_id) REFERENCES companies(id)
            )
        ");
        
        // Insert default data
        $company_id = 'default-company-' . uniqid();
        $pdo->exec("
            INSERT OR IGNORE INTO companies (id, name) 
            VALUES ('$company_id', 'Domyślna Firma')
        ");
        
        // Insert default users
        $default_users = [
            [
                'id' => 'owner-' . uniqid(),
                'username' => 'owner',
                'password_hash' => password_hash('owner123', PASSWORD_DEFAULT),
                'type' => 'owner',
                'role' => 'owner',
                'company_id' => null,
                'company_name' => 'System Admin'
            ],
            [
                'id' => 'admin-' . uniqid(),
                'username' => 'admin',
                'password_hash' => password_hash('admin123', PASSWORD_DEFAULT),
                'type' => 'admin',
                'role' => 'admin',
                'company_id' => $company_id,
                'company_name' => 'Domyślna Firma'
            ],
            [
                'id' => 'user-' . uniqid(),
                'username' => 'user',
                'password_hash' => password_hash('user123', PASSWORD_DEFAULT),
                'type' => 'user',
                'role' => 'user',
                'company_id' => $company_id,
                'company_name' => 'Domyślna Firma'
            ]
        ];
        
        foreach ($default_users as $user) {
            $stmt = $pdo->prepare("
                INSERT OR IGNORE INTO users (id, username, password_hash, type, role, company_id, company_name)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ");
            $stmt->execute([
                $user['id'], $user['username'], $user['password_hash'], 
                $user['type'], $user['role'], $user['company_id'], $user['company_name']
            ]);
        }
        
        return true;
        
    } catch (Exception $e) {
        throw new Exception("Database initialization failed: " . $e->getMessage());
    }
}

// Main execution
try {
    init_database();
    
    $response = [
        'message' => 'Database initialized successfully',
        'status' => 'ready',
        'default_accounts' => [
            'owner' => 'owner/owner123',
            'admin' => 'admin/admin123',
            'user' => 'user/user123'
        ]
    ];
    
    echo json_encode($response);
    
} catch (Exception $e) {
    http_response_code(500);
    echo json_encode([
        'message' => 'Database initialization failed: ' . $e->getMessage(),
        'status' => 'error'
    ]);
}
?>