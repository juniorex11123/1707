#!/usr/bin/env python3
"""
QR Generate endpoint for TimeTracker Pro
URL: https://timetrackerpro.pl/qr_generate.py3?employee_id=123
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils import handle_cors_preflight, get_request_method, get_query_params, error_response, success_response, require_auth, init_database
from database import Database
import qrcode
import io
import base64

def generate_qr_code(data: str) -> str:
    """Generate QR code and return base64 encoded image"""
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(data)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    img_str = base64.b64encode(buf.getvalue()).decode()
    return img_str

def main():
    handle_cors_preflight()
    init_database()
    
    db = Database()
    
    if get_request_method() != 'GET':
        error_response("Method not allowed", 405)
    
    user = require_auth(['owner', 'admin'])
    
    params = get_query_params()
    employee_id = params.get('employee_id')
    
    if not employee_id:
        error_response("employee_id parameter required", 400)
    
    employee = db.find_one("employees", {"id": employee_id})
    if not employee:
        error_response("Employee not found", 404)
    
    qr_image = generate_qr_code(employee["qr_code"])
    
    response = {
        "qr_code_data": employee["qr_code"],
        "qr_code_image": qr_image
    }
    
    success_response(response)

if __name__ == "__main__":
    main()