#!/usr/bin/env python3
"""
Database initialization endpoint for TimeTracker Pro
URL: https://TWOJA-DOMENA.home.pl/init.py3
Run this once to initialize the database
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from utils import handle_cors_preflight, get_request_method, success_response, init_database
    
    def main():
        handle_cors_preflight()
        
        try:
            init_database()
            success_response({
                "message": "Database initialized successfully",
                "status": "ready",
                "default_accounts": {
                    "owner": "owner/owner123",
                    "admin": "admin/admin123", 
                    "user": "user/user123"
                }
            })
        except Exception as e:
            success_response({
                "message": f"Database initialization failed: {str(e)}",
                "status": "error"
            }, 500)

    if __name__ == "__main__":
        main()

except ImportError as e:
    # If utils import fails, provide basic initialization
    import sqlite3
    import json
    from datetime import datetime
    
    print("Status: 200 OK")
    print("Content-Type: application/json")
    print("Access-Control-Allow-Origin: *")
    print("Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS")
    print("Access-Control-Allow-Headers: Content-Type, Authorization")
    print()
    
    try:
        # Basic database initialization without utils
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
        
        conn.commit()
        conn.close()
        
        print(json.dumps({
            "message": "Database initialized successfully (basic mode)",
            "status": "ready",
            "note": "Please check utils.py file for import errors",
            "error": str(e)
        }))
        
    except Exception as db_error:
        print(json.dumps({
            "message": f"Database initialization failed: {str(db_error)}",
            "status": "error",
            "import_error": str(e)
        }))