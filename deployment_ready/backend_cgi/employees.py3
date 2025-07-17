#!/usr/bin/env python3
"""
Employees endpoint for TimeTracker Pro
URL: https://timetrackerpro.pl/employees.py3
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils import handle_cors_preflight, get_request_method, get_request_body, get_query_params, error_response, success_response, require_auth, init_database
from auth import parse_datetime
from database import Database
import uuid

def main():
    handle_cors_preflight()
    init_database()
    
    db = Database()
    method = get_request_method()
    
    if method == 'GET':
        # Get employees
        user = require_auth(['owner', 'admin', 'user'])
        
        if user["type"] == "owner":
            employees = db.find_many("employees")
        else:
            employees = db.find_many("employees", {"company_id": user["company_id"]})
        
        # Parse datetime fields
        for employee in employees:
            employee["created_at"] = parse_datetime(employee["created_at"]).isoformat()
        
        success_response(employees)
    
    elif method == 'POST':
        # Create employee
        user = require_auth(['owner', 'admin'])
        
        body = get_request_body()
        if not body:
            error_response("Request body required", 400)
        
        name = body.get('name')
        company_id = body.get('company_id')
        
        if not name or not company_id:
            error_response("Name and company_id required", 400)
        
        # Generate QR code
        qr_code = f"QR-EMP-{str(uuid.uuid4())[:8].upper()}"
        
        employee = {
            "id": str(uuid.uuid4()),
            "name": name,
            "qr_code": qr_code,
            "company_id": company_id,
            "is_active": True,
            "created_at": datetime.utcnow().isoformat()
        }
        
        db.insert_one("employees", employee)
        
        success_response(employee, 201)
    
    else:
        error_response("Method not allowed", 405)

if __name__ == "__main__":
    from datetime import datetime
    main()