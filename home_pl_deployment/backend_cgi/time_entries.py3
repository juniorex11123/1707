#!/usr/bin/env python3
"""
Time Entries endpoint for TimeTracker Pro
URL: https://timetrackerpro.pl/time_entries.py3
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils import handle_cors_preflight, get_request_method, get_request_body, error_response, success_response, require_auth, init_database
from auth import parse_datetime
from database import Database

def main():
    handle_cors_preflight()
    init_database()
    
    db = Database()
    
    if get_request_method() != 'GET':
        error_response("Method not allowed", 405)
    
    user = require_auth(['owner', 'admin', 'user'])
    
    # Get time entries
    if user["type"] == "owner":
        time_entries = db.find_many("time_entries")
    else:
        # Get employees from user's company first
        employees = db.find_many("employees", {"company_id": user["company_id"]})
        employee_ids = [emp["id"] for emp in employees]
        time_entries = db.find_time_entries_by_employee_ids(employee_ids)
    
    # Parse datetime fields
    for entry in time_entries:
        entry["check_in"] = parse_datetime(entry["check_in"]).isoformat()
        if entry["check_out"]:
            entry["check_out"] = parse_datetime(entry["check_out"]).isoformat()
        entry["created_at"] = parse_datetime(entry["created_at"]).isoformat()
    
    success_response(time_entries)

if __name__ == "__main__":
    main()