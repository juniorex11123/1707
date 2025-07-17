#!/usr/bin/env python3
"""
Companies endpoint for TimeTracker Pro
URL: https://timetrackerpro.pl/companies.py3
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils import handle_cors_preflight, get_request_method, get_request_body, error_response, success_response, require_auth, init_database
from auth import parse_datetime
from database import Database
from datetime import datetime
import uuid

def main():
    handle_cors_preflight()
    init_database()
    
    db = Database()
    method = get_request_method()
    
    if method == 'GET':
        # Get companies (owner only)
        user = require_auth(['owner'])
        
        companies = db.find_many("companies")
        
        # Parse datetime fields
        for company in companies:
            company["created_at"] = parse_datetime(company["created_at"]).isoformat()
        
        success_response(companies)
    
    elif method == 'POST':
        # Create company (owner only)
        user = require_auth(['owner'])
        
        body = get_request_body()
        if not body:
            error_response("Request body required", 400)
        
        name = body.get('name')
        if not name:
            error_response("Name required", 400)
        
        company = {
            "id": str(uuid.uuid4()),
            "name": name,
            "created_at": datetime.utcnow().isoformat()
        }
        
        db.insert_one("companies", company)
        
        success_response(company, 201)
    
    else:
        error_response("Method not allowed", 405)

if __name__ == "__main__":
    main()