#!/usr/bin/env python3
"""
Login endpoint for TimeTracker Pro
URL: https://timetrackerpro.pl/login.py3
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils import handle_cors_preflight, get_request_method, get_request_body, output_json, error_response, success_response, init_database
from auth import verify_password, create_access_token, parse_datetime
from database import Database

def main():
    handle_cors_preflight()
    init_database()
    
    db = Database()
    
    if get_request_method() != 'POST':
        error_response("Method not allowed", 405)
    
    body = get_request_body()
    if not body:
        error_response("Request body required", 400)
    
    username = body.get('username')
    password = body.get('password')
    
    if not username or not password:
        error_response("Username and password required", 400)
    
    # Find user
    user = db.find_one("users", {"username": username})
    if not user or not verify_password(password, user["password_hash"]):
        error_response("Invalid credentials", 401)
    
    # Create access token
    access_token = create_access_token({"user_id": user["id"]})
    
    # Get company name if user belongs to a company
    company_name = user.get("company_name")
    if user.get("company_id"):
        company = db.find_one("companies", {"id": user["company_id"]})
        if company:
            company_name = company["name"]
    
    # Parse datetime
    created_at = parse_datetime(user["created_at"]) if isinstance(user["created_at"], str) else user["created_at"]
    
    user_response = {
        "id": user["id"],
        "username": user["username"],
        "type": user["type"],
        "role": user["role"],
        "company_id": user.get("company_id"),
        "company_name": company_name,
        "created_at": created_at.isoformat() if isinstance(created_at, object) else created_at
    }
    
    response = {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user_response
    }
    
    success_response(response)

if __name__ == "__main__":
    main()