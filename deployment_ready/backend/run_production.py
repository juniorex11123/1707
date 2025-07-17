#!/usr/bin/env python3
"""
Production runner for TimeTracker Pro Backend
"""
import os
import uvicorn
from pathlib import Path

# Set environment to production
os.environ['ENVIRONMENT'] = 'production'

# Load production environment variables
env_file = Path(__file__).parent / '.env.production'
if env_file.exists():
    from dotenv import load_dotenv
    load_dotenv(env_file)

if __name__ == "__main__":
    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=8001,
        workers=4,
        log_level="info",
        access_log=True,
        reload=False
    )