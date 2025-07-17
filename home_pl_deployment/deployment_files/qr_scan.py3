#!/usr/bin/env python3
"""
QR Scan endpoint for TimeTracker Pro
URL: https://timetrackerpro.pl/qr_scan.py3
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
    
    if get_request_method() != 'POST':
        error_response("Method not allowed", 405)
    
    user = require_auth(['owner', 'admin', 'user'])
    
    body = get_request_body()
    if not body:
        error_response("Request body required", 400)
    
    qr_code = body.get('qr_code')
    if not qr_code:
        error_response("QR code required", 400)
    
    try:
        # Find employee by QR code
        employee = db.find_one("employees", {"qr_code": qr_code})
        
        if not employee:
            success_response({
                "success": False,
                "message": "QR kod nie istnieje"
            })
        
        # Check if employee belongs to the same company as the user
        if str(employee.get("company_id")) != str(user.get("company_id")):
            success_response({
                "success": False,
                "message": "QR kod nie należy do Twojej firmy"
            })
        
        # Check if employee is active
        if not employee.get("is_active", True):
            success_response({
                "success": False,
                "message": "Pracownik jest nieaktywny"
            })
        
        # Get today's date
        today = datetime.utcnow().strftime("%Y-%m-%d")
        
        # Find the last time entry for this employee today
        last_entry = db.find_last_time_entry(employee["id"], today)
        
        now = datetime.utcnow()
        
        # Determine if this is check-in or check-out
        if not last_entry or last_entry.get("check_out"):
            # This is check-in
            action = "check_in"
            action_text = "Rozpoczęto pracę"
            
            # Create new time entry
            time_entry = {
                "id": str(uuid.uuid4()),
                "employee_id": employee["id"],
                "check_in": now.isoformat(),
                "check_out": None,
                "date": today,
                "total_hours": None,
                "created_at": now.isoformat()
            }
            
            db.insert_one("time_entries", time_entry)
            
        else:
            # This is check-out
            action = "check_out"
            action_text = "Zakończono pracę"
            
            # Update existing time entry
            check_in = parse_datetime(last_entry["check_in"])
            
            delta = now - check_in
            total_hours = delta.total_seconds() / 3600
            
            db.update_one(
                "time_entries",
                {"id": last_entry["id"]},
                {
                    "check_out": now.isoformat(),
                    "total_hours": total_hours
                }
            )
        
        success_response({
            "success": True,
            "action": action,
            "employee_name": employee["name"],
            "time": now.strftime("%Y-%m-%d %H:%M:%S"),
            "message": f"{action_text} dla {employee['name']}",
            "cooldown_seconds": 5
        })
        
    except Exception as e:
        success_response({
            "success": False,
            "message": "Błąd podczas przetwarzania skanowania QR"
        })

if __name__ == "__main__":
    main()