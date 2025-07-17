#!/usr/bin/env python3
import json
import sqlite3
import os
from datetime import datetime

print("Status: 200 OK")
print("Content-Type: application/json")
print("Access-Control-Allow-Origin: *")
print("Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS")
print("Access-Control-Allow-Headers: Content-Type, Authorization")
print()

try:
    # Create database
    db_path = "timetracker_pro.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create tables
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            type TEXT NOT NULL,
            role TEXT NOT NULL,
            company_id TEXT,
            company_name TEXT,
            created_at TEXT NOT NULL
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS companies (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS employees (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            qr_code TEXT UNIQUE NOT NULL,
            company_id TEXT NOT NULL,
            is_active BOOLEAN DEFAULT TRUE,
            created_at TEXT NOT NULL
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS time_entries (
            id TEXT PRIMARY KEY,
            employee_id TEXT NOT NULL,
            check_in TEXT NOT NULL,
            check_out TEXT,
            date TEXT NOT NULL,
            total_hours REAL,
            created_at TEXT NOT NULL
        )
    """)
    
    # Create default users if not exist
    cursor.execute("SELECT COUNT(*) FROM users WHERE username = 'owner'")
    if cursor.fetchone()[0] == 0:
        import hashlib
        
        # Simple password hashing (bcrypt would be better, but this works)
        def simple_hash(password):
            return hashlib.sha256(password.encode()).hexdigest()
        
        now = datetime.utcnow().isoformat()
        
        # Insert default users
        users = [
            ("1", "owner", simple_hash("owner123"), "owner", "owner", None, "System Owner", now),
            ("2", "admin", simple_hash("admin123"), "admin", "admin", "1", "Firma ABC", now),
            ("3", "user", simple_hash("user123"), "user", "user", "1", "Firma ABC", now)
        ]
        
        cursor.executemany("""
            INSERT INTO users (id, username, password_hash, type, role, company_id, company_name, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, users)
        
        # Insert default companies
        companies = [
            ("1", "Firma ABC", now),
            ("2", "Firma XYZ", now)
        ]
        
        cursor.executemany("""
            INSERT INTO companies (id, name, created_at)
            VALUES (?, ?, ?)
        """, companies)
        
        # Insert default employees
        employees = [
            ("1", "Jan Kowalski", "QR-EMP-001", "1", True, now),
            ("2", "Anna Nowak", "QR-EMP-002", "1", True, now)
        ]
        
        cursor.executemany("""
            INSERT INTO employees (id, name, qr_code, company_id, is_active, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, employees)
    
    conn.commit()
    conn.close()
    
    result = {
        "message": "Database initialized successfully",
        "status": "ready",
        "default_accounts": {
            "owner": "owner/owner123",
            "admin": "admin/admin123", 
            "user": "user/user123"
        },
        "database_path": db_path,
        "note": "Simple hash used for passwords"
    }
    
except Exception as e:
    result = {
        "message": f"Database initialization failed: {str(e)}",
        "status": "error"
    }

print(json.dumps(result, indent=2))