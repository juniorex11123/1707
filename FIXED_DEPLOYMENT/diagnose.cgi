#!/usr/bin/env python3
"""
Diagnostic script for TimeTracker Pro
URL: https://TWOJA-DOMENA.home.pl/diagnose.py3
"""
import sys
import os
import json

print("Status: 200 OK")
print("Content-Type: application/json")
print("Access-Control-Allow-Origin: *")
print()

try:
    # Check Python version
    python_version = sys.version
    
    # Check if files exist
    current_dir = os.path.dirname(os.path.abspath(__file__))
    files_to_check = [
        'utils.py', 'utils.py3', 'auth.py', 'auth.py3', 
        'database.py', 'database.py3', 'login.py3', 'init.py3'
    ]
    
    file_status = {}
    for file in files_to_check:
        file_path = os.path.join(current_dir, file)
        file_status[file] = os.path.exists(file_path)
        
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                first_line = f.readline().strip()
                file_status[f"{file}_first_line"] = first_line
    
    # Try to import utils
    try:
        sys.path.insert(0, current_dir)
        import utils
        utils_import = "SUCCESS"
    except Exception as e:
        utils_import = f"FAILED: {str(e)}"
    
    # Try to import auth
    try:
        import auth
        auth_import = "SUCCESS"
    except Exception as e:
        auth_import = f"FAILED: {str(e)}"
    
    # Try to import database
    try:
        import database
        database_import = "SUCCESS"
    except Exception as e:
        database_import = f"FAILED: {str(e)}"
    
    result = {
        "status": "diagnostic_complete",
        "python_version": python_version,
        "current_directory": current_dir,
        "file_status": file_status,
        "import_status": {
            "utils": utils_import,
            "auth": auth_import,
            "database": database_import
        },
        "environment": {
            "REQUEST_METHOD": os.environ.get('REQUEST_METHOD', 'Not set'),
            "SCRIPT_NAME": os.environ.get('SCRIPT_NAME', 'Not set'),
            "PATH_INFO": os.environ.get('PATH_INFO', 'Not set')
        }
    }
    
    print(json.dumps(result, indent=2))
    
except Exception as e:
    print(json.dumps({
        "status": "diagnostic_failed",
        "error": str(e)
    }))