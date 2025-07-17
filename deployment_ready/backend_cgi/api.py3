#!/usr/bin/env python3
"""
Main API endpoint for TimeTracker Pro
URL: https://timetrackerpro.pl/api.py3
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils import handle_cors_preflight, get_request_method, success_response, init_database

def main():
    handle_cors_preflight()
    init_database()
    
    if get_request_method() == 'GET':
        success_response({"message": "TimeTracker Pro API is running"})
    else:
        success_response({"message": "TimeTracker Pro API is running"})

if __name__ == "__main__":
    main()