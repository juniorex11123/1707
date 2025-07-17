#!/usr/bin/env python3
"""
Users endpoint for TimeTracker Pro
URL: https://timetrackerpro.pl/users.py3
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils import handle_cors_preflight, get_request_method, get_request_body, error_response, success_response, require_auth, init_database
from auth import hash_password, parse_datetime
from database import Database
from datetime import datetime
import uuid

def main():
    handle_cors_preflight()
    init_database()
    
    db = Database()
    method = get_request_method()
    
    if method == 'GET':
        # Get users
        user = require_auth(['owner', 'admin'])
        
        if user["type"] == "owner":
            users = db.find_many("users")
        elif user["type"] == "admin":
            # Admin can only see users from their company
            users = db.find_many("users", {"company_id": user["company_id"]})
        
        user_responses = []
        for user_data in users:
            company_name = user_data.get("company_name")
            if user_data.get("company_id"):
                company = db.find_one("companies", {"id": user_data["company_id"]})
                if company:
                    company_name = company["name"]
            
            created_at = parse_datetime(user_data["created_at"]) if isinstance(user_data["created_at"], str) else user_data["created_at"]
            
            user_responses.append({
                "id": user_data["id"],
                "username": user_data["username"],
                "type": user_data["type"],
                "role": user_data["role"],
                "company_id": user_data.get("company_id"),
                "company_name": company_name,
                "created_at": created_at.isoformat()
            })
        
        success_response(user_responses)
    
    elif method == 'POST':
        # Create user
        user = require_auth(['owner', 'admin'])
        
        body = get_request_body()
        if not body:
            error_response("Request body required", 400)
        
        username = body.get('username')
        password = body.get('password')
        user_type = body.get('type')
        company_id = body.get('company_id')
        
        if not username or not password or not user_type:
            error_response("Username, password and type required", 400)
        
        # Check permissions
        if user["type"] == "admin":
            if not company_id:
                company_id = user["company_id"]
            elif company_id != user["company_id"]:
                error_response("Cannot create users for other companies", 403)
            if user_type == "owner":
                error_response("Cannot create owner accounts", 403)
        
        # Check if username already exists
        existing_user = db.find_one("users", {"username": username})
        if existing_user:
            error_response("Username already exists", 400)
        
        # Get company name if provided
        company_name = None
        if company_id:
            company = db.find_one("companies", {"id": company_id})
            if company:
                company_name = company["name"]
        
        new_user = {
            "id": str(uuid.uuid4()),
            "username": username,
            "password_hash": hash_password(password),
            "type": user_type,
            "role": user_type,
            "company_id": company_id,
            "company_name": company_name,
            "created_at": datetime.utcnow().isoformat()
        }
        
        db.insert_one("users", new_user)
        
        response = {
            "id": new_user["id"],
            "username": new_user["username"],
            "type": new_user["type"],
            "role": new_user["role"],
            "company_id": new_user["company_id"],
            "company_name": company_name,
            "created_at": new_user["created_at"]
        }
        
        success_response(response, 201)
    
    else:
        error_response("Method not allowed", 405)

if __name__ == "__main__":
    main()