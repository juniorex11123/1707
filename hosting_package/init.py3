#!/usr/bin/env python3
"""
Database initialization endpoint for TimeTracker Pro
URL: https://timetrackerpro.pl/init.py3
Run this once to initialize the database
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

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