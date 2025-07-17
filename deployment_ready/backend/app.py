#!/usr/bin/env python3
"""
WSGI entry point for TimeTracker Pro Backend
Kompatybilny z home.pl hosting
"""
import os
import sys
from pathlib import Path

# Add current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

# Set environment variables
os.environ.setdefault('DB_PATH', './timetracker_pro.db')
os.environ.setdefault('JWT_SECRET', 'your-super-secret-jwt-key-for-production-2025')
os.environ.setdefault('CORS_ORIGINS', '["https://timetrackerpro.pl", "https://www.timetrackerpro.pl"]')

# Import the FastAPI app
from server import app

# For compatibility with some hosting providers
application = app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)