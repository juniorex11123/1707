#!/usr/bin/env python3
"""
Authentication module for TimeTracker Pro
Compatible with home.pl CGI hosting
"""
import os
import jwt
import bcrypt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from database import Database

# Configuration
JWT_SECRET = os.environ.get('JWT_SECRET', 'your-super-secret-jwt-key-for-production-2025')
JWT_ALGORITHM = 'HS256'
JWT_EXPIRATION_HOURS = 24

db = Database()

def hash_password(password: str) -> str:
    """Hash a password"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password: str, password_hash: str) -> bool:
    """Verify a password against its hash"""
    return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))

def create_access_token(data: dict) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> Optional[Dict[str, Any]]:
    """Verify JWT token"""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.JWTError:
        return None

def get_current_user(token: str) -> Optional[Dict[str, Any]]:
    """Get current user from token"""
    payload = verify_token(token)
    if not payload:
        return None
    
    user_id = payload.get("user_id")
    if not user_id:
        return None
    
    user = db.find_one("users", {"id": user_id})
    return user

def parse_datetime(datetime_str: str) -> datetime:
    """Parse datetime string to datetime object"""
    if isinstance(datetime_str, str):
        return datetime.fromisoformat(datetime_str.replace('Z', '+00:00'))
    return datetime_str

def init_default_data():
    """Initialize default data if not exists"""
    # Check if owner exists
    owner = db.find_one("users", {"username": "owner"})
    if not owner:
        # Create default users
        default_users = [
            {
                "id": "1",
                "username": "owner",
                "password_hash": hash_password("owner123"),
                "type": "owner",
                "role": "owner",
                "company_id": None,
                "company_name": "System Owner",
                "created_at": datetime.utcnow().isoformat()
            },
            {
                "id": "2",
                "username": "admin",
                "password_hash": hash_password("admin123"),
                "type": "admin",
                "role": "admin",
                "company_id": "1",
                "company_name": "Firma ABC",
                "created_at": datetime.utcnow().isoformat()
            },
            {
                "id": "3",
                "username": "user",
                "password_hash": hash_password("user123"),
                "type": "user",
                "role": "user",
                "company_id": "1",
                "company_name": "Firma ABC",
                "created_at": datetime.utcnow().isoformat()
            }
        ]
        db.insert_many("users", default_users)
        
        # Create default companies
        default_companies = [
            {
                "id": "1",
                "name": "Firma ABC",
                "created_at": datetime.utcnow().isoformat()
            },
            {
                "id": "2",
                "name": "Firma XYZ",
                "created_at": datetime.utcnow().isoformat()
            }
        ]
        db.insert_many("companies", default_companies)
        
        # Create default employees
        default_employees = [
            {
                "id": "1",
                "name": "Jan Kowalski",
                "qr_code": "QR-EMP-001",
                "company_id": "1",
                "is_active": True,
                "created_at": datetime.utcnow().isoformat()
            },
            {
                "id": "2",
                "name": "Anna Nowak",
                "qr_code": "QR-EMP-002",
                "company_id": "1",
                "is_active": True,
                "created_at": datetime.utcnow().isoformat()
            }
        ]
        db.insert_many("employees", default_employees)
        
        # Create default time entries
        default_time_entries = [
            {
                "id": "1",
                "employee_id": "1",
                "check_in": datetime.utcnow().replace(hour=8, minute=0, second=0).isoformat(),
                "check_out": datetime.utcnow().replace(hour=16, minute=0, second=0).isoformat(),
                "date": datetime.utcnow().strftime("%Y-%m-%d"),
                "total_hours": 8.0,
                "created_at": datetime.utcnow().isoformat()
            },
            {
                "id": "2",
                "employee_id": "2",
                "check_in": datetime.utcnow().replace(hour=9, minute=0, second=0).isoformat(),
                "check_out": datetime.utcnow().replace(hour=17, minute=0, second=0).isoformat(),
                "date": datetime.utcnow().strftime("%Y-%m-%d"),
                "total_hours": 8.0,
                "created_at": datetime.utcnow().isoformat()
            }
        ]
        db.insert_many("time_entries", default_time_entries)