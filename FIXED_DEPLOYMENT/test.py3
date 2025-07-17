#!/usr/bin/env python3
import json
import os

print("Status: 200 OK")
print("Content-Type: application/json")
print("Access-Control-Allow-Origin: *")
print()

result = {
    "message": "CGI Test Successful",
    "status": "working",
    "python_version": "3.x",
    "request_method": os.environ.get('REQUEST_METHOD', 'GET'),
    "script_name": os.environ.get('SCRIPT_NAME', ''),
    "server_software": os.environ.get('SERVER_SOFTWARE', 'Unknown')
}

print(json.dumps(result, indent=2))