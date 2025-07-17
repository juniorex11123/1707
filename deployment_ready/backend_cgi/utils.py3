#!/usr/bin/env python3
"""
Utility functions for TimeTracker Pro CGI
Compatible with home.pl CGI hosting
"""
import json
import os
import sys
from datetime import datetime
from typing import Dict, Any, Optional

def output_json(data: Any, status_code: int = 200):
    """Output JSON response with proper headers"""
    status_messages = {
        200: "200 OK",
        201: "201 Created", 
        400: "400 Bad Request",
        401: "401 Unauthorized",
        403: "403 Forbidden",
        404: "404 Not Found",
        500: "500 Internal Server Error"
    }
    
    print(f"Status: {status_messages.get(status_code, '200 OK')}")
    print("Content-Type: application/json")
    print("Access-Control-Allow-Origin: https://timetrackerpro.pl")
    print("Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS")
    print("Access-Control-Allow-Headers: Content-Type, Authorization")
    print("Access-Control-Allow-Credentials: true")
    print()  # Empty line to separate headers from body
    
    if isinstance(data, dict) or isinstance(data, list):
        print(json.dumps(data, default=str))
    else:
        print(json.dumps({"message": str(data)}))

def get_request_method() -> str:
    """Get HTTP request method"""
    return os.environ.get('REQUEST_METHOD', 'GET')

def get_request_body() -> Optional[Dict[str, Any]]:
    """Get request body as JSON"""
    try:
        content_length = int(os.environ.get('CONTENT_LENGTH', '0'))
        if content_length > 0:
            body = sys.stdin.read(content_length)
            return json.loads(body)
    except (ValueError, json.JSONDecodeError):
        pass
    return None

def get_query_params() -> Dict[str, str]:
    """Get query parameters from URL"""
    query_string = os.environ.get('QUERY_STRING', '')
    params = {}
    
    if query_string:
        for param in query_string.split('&'):
            if '=' in param:
                key, value = param.split('=', 1)
                params[key] = value
    
    return params

def get_auth_token() -> Optional[str]:
    """Get authorization token from headers"""
    auth_header = os.environ.get('HTTP_AUTHORIZATION', '')
    if auth_header.startswith('Bearer '):
        return auth_header[7:]  # Remove 'Bearer ' prefix
    return None

def handle_cors_preflight():
    """Handle CORS preflight requests"""
    if get_request_method() == 'OPTIONS':
        print("Status: 200 OK")
        print("Access-Control-Allow-Origin: https://timetrackerpro.pl")
        print("Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS")
        print("Access-Control-Allow-Headers: Content-Type, Authorization")
        print("Access-Control-Allow-Credentials: true")
        print()
        sys.exit(0)

def error_response(message: str, status_code: int = 400):
    """Output error response"""
    output_json({"error": message}, status_code)
    sys.exit(1)

def success_response(data: Any, status_code: int = 200):
    """Output success response"""
    output_json(data, status_code)
    sys.exit(0)

def require_auth(required_roles: list = None):
    """Decorator to require authentication"""
    from auth import get_current_user
    
    token = get_auth_token()
    if not token:
        error_response("Authorization required", 401)
    
    user = get_current_user(token)
    if not user:
        error_response("Invalid token", 401)
    
    if required_roles and user.get("type") not in required_roles:
        error_response("Access denied", 403)
    
    return user

def init_database():
    """Initialize database and default data"""
    from database import Database
    from auth import init_default_data
    
    db = Database()
    db.init_db()
    init_default_data()