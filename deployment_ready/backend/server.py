from fastapi import FastAPI, APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.gzip import GZipMiddleware
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional
import uuid
from datetime import datetime, timedelta
import jwt
import bcrypt
import qrcode
import io
import base64
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from fastapi.responses import Response
import asyncio
from functools import lru_cache
from database import Database
import json

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# SQLite Database connection
db_path = os.environ.get('DB_PATH', './timetracker_pro.db')
db = Database(db_path)

# JWT Configuration
JWT_SECRET = os.environ.get('JWT_SECRET', 'your-secret-key-here')
JWT_ALGORITHM = 'HS256'
JWT_EXPIRATION_HOURS = 24

# Security
security = HTTPBearer()

# Create the main app without a prefix
app = FastAPI(
    title="TimeTracker Pro API", 
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Add GZip middleware for compression
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# === CACHE SYSTEM === 
# Simple cache for frequently accessed data
from functools import wraps
import time

cache = {}
CACHE_DURATION = 300  # 5 minutes

def cached(duration=CACHE_DURATION):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Create cache key
            cache_key = f"{func.__name__}:{str(args)}:{str(kwargs)}"
            
            # Check if data is in cache
            if cache_key in cache:
                data, timestamp = cache[cache_key]
                if time.time() - timestamp < duration:
                    return data
            
            # Execute function and save to cache
            result = await func(*args, **kwargs)
            cache[cache_key] = (result, time.time())
            return result
        return wrapper
    return decorator

# === MODELS ===

class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    username: str
    password_hash: str
    type: str  # 'owner', 'admin', 'user'
    role: str  # same as type for compatibility
    company_id: Optional[str] = None
    company_name: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class UserCreate(BaseModel):
    username: str
    password: str
    type: str
    company_id: Optional[str] = None

class UserUpdate(BaseModel):
    username: Optional[str] = None
    password: Optional[str] = None
    type: Optional[str] = None
    company_id: Optional[str] = None

class UserResponse(BaseModel):
    id: str
    username: str
    type: str
    role: str
    company_id: Optional[str] = None
    company_name: Optional[str] = None
    created_at: datetime

class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

class Company(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

class CompanyCreate(BaseModel):
    name: str

class CompanyUpdate(BaseModel):
    name: Optional[str] = None

class Employee(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    qr_code: str
    company_id: str
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)

class EmployeeCreate(BaseModel):
    name: str
    company_id: str

class EmployeeUpdate(BaseModel):
    name: Optional[str] = None
    is_active: Optional[bool] = None

class TimeEntry(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    employee_id: str
    check_in: datetime
    check_out: Optional[datetime] = None
    date: str
    total_hours: Optional[float] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class TimeEntryCreate(BaseModel):
    employee_id: str
    check_in: datetime
    check_out: Optional[datetime] = None

class TimeEntryUpdate(BaseModel):
    check_in: Optional[datetime] = None
    check_out: Optional[datetime] = None

class StatusCheck(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_name: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class StatusCheckCreate(BaseModel):
    client_name: str

class QRResponse(BaseModel):
    qr_code_data: str
    qr_code_image: str  # base64 encoded image

class QRScanRequest(BaseModel):
    qr_code: str
    user_id: str

class QRScanResponse(BaseModel):
    success: bool
    action: Optional[str] = None
    employee_name: Optional[str] = None
    time: Optional[str] = None
    message: str
    cooldown_seconds: Optional[int] = None

# === UTILITY FUNCTIONS ===

@lru_cache(maxsize=128)
def hash_password(password: str) -> str:
    """Hash a password with cache"""
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

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """Verify JWT token"""
    try:
        payload = jwt.decode(credentials.credentials, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

@cached(duration=1800)  # 30 minutes cache
async def get_current_user(token_payload: dict = Depends(verify_token)) -> dict:
    """Get current user from token with cache"""
    user_id = token_payload.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user = await db.find_one("users", {"id": user_id})
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    return user

@lru_cache(maxsize=64)
def generate_qr_code(data: str) -> str:
    """Generate QR code and return base64 encoded image with cache"""
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(data)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    img_str = base64.b64encode(buf.getvalue()).decode()
    return img_str

def parse_datetime(datetime_str: str) -> datetime:
    """Parse datetime string to datetime object"""
    if isinstance(datetime_str, str):
        return datetime.fromisoformat(datetime_str.replace('Z', '+00:00'))
    return datetime_str

# === INITIALIZATION ===

async def init_default_data():
    """Initialize default data if not exists"""
    # Check if owner exists
    owner = await db.find_one("users", {"username": "owner"})
    if not owner:
        # Create default users
        default_users = [
            {
                "id": str(uuid.uuid4()),
                "username": "owner",
                "password_hash": hash_password("owner123"),
                "type": "owner",
                "role": "owner",
                "company_id": None,
                "company_name": "System Owner",
                "created_at": datetime.utcnow()
            },
            {
                "id": str(uuid.uuid4()),
                "username": "admin",
                "password_hash": hash_password("admin123"),
                "type": "admin",
                "role": "admin",
                "company_id": "1",
                "company_name": "Firma ABC",
                "created_at": datetime.utcnow()
            },
            {
                "id": str(uuid.uuid4()),
                "username": "user",
                "password_hash": hash_password("user123"),
                "type": "user",
                "role": "user",
                "company_id": "1",
                "company_name": "Firma ABC",
                "created_at": datetime.utcnow()
            }
        ]
        await db.insert_many("users", default_users)
        
        # Create default companies
        default_companies = [
            {
                "id": "1",
                "name": "Firma ABC",
                "created_at": datetime.utcnow()
            },
            {
                "id": "2",
                "name": "Firma XYZ",
                "created_at": datetime.utcnow()
            }
        ]
        await db.insert_many("companies", default_companies)
        
        # Create default employees
        default_employees = [
            {
                "id": "1",
                "name": "Jan Kowalski",
                "qr_code": "QR-EMP-001",
                "company_id": "1",
                "is_active": True,
                "created_at": datetime.utcnow()
            },
            {
                "id": "2",
                "name": "Anna Nowak",
                "qr_code": "QR-EMP-002",
                "company_id": "1",
                "is_active": True,
                "created_at": datetime.utcnow()
            }
        ]
        await db.insert_many("employees", default_employees)
        
        # Create default time entries
        default_time_entries = [
            {
                "id": "1",
                "employee_id": "1",
                "check_in": datetime.utcnow().replace(hour=8, minute=0, second=0),
                "check_out": datetime.utcnow().replace(hour=16, minute=0, second=0),
                "date": datetime.utcnow().strftime("%Y-%m-%d"),
                "total_hours": 8.0,
                "created_at": datetime.utcnow()
            },
            {
                "id": "2",
                "employee_id": "2",
                "check_in": datetime.utcnow().replace(hour=9, minute=0, second=0),
                "check_out": datetime.utcnow().replace(hour=17, minute=0, second=0),
                "date": datetime.utcnow().strftime("%Y-%m-%d"),
                "total_hours": 8.0,
                "created_at": datetime.utcnow()
            }
        ]
        await db.insert_many("time_entries", default_time_entries)

# === AUTHENTICATION ROUTES ===

@api_router.post("/auth/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """User login - optimized"""
    user = await db.find_one("users", {"username": request.username})
    if not user or not verify_password(request.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Create access token
    access_token = create_access_token({"user_id": user["id"]})
    
    # Get company name if user belongs to a company
    company_name = user.get("company_name")
    if user.get("company_id"):
        company = await db.find_one("companies", {"id": user["company_id"]})
        if company:
            company_name = company["name"]
    
    # Parse datetime
    created_at = parse_datetime(user["created_at"]) if isinstance(user["created_at"], str) else user["created_at"]
    
    user_response = UserResponse(
        id=user["id"],
        username=user["username"],
        type=user["type"],
        role=user["role"],
        company_id=user.get("company_id"),
        company_name=company_name,
        created_at=created_at
    )
    
    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        user=user_response
    )

# === COMPANY ROUTES ===

@api_router.get("/companies", response_model=List[Company])
@cached(duration=300)  # 5 minutes cache
async def get_companies(current_user: dict = Depends(get_current_user)):
    """Get all companies (owner only) with cache"""
    if current_user["type"] != "owner":
        raise HTTPException(status_code=403, detail="Access denied")
    
    companies = await db.find_many("companies")
    
    # Parse datetime fields
    for company in companies:
        company["created_at"] = parse_datetime(company["created_at"])
    
    return companies

@api_router.post("/companies", response_model=Company)
async def create_company(company: CompanyCreate, current_user: dict = Depends(get_current_user)):
    """Create new company (owner only)"""
    if current_user["type"] != "owner":
        raise HTTPException(status_code=403, detail="Access denied")
    
    company_obj = Company(**company.dict())
    await db.insert_one("companies", company_obj.dict())
    
    # Clear cache
    cache.clear()
    
    return company_obj

@api_router.put("/companies/{company_id}", response_model=Company)
async def update_company(company_id: str, company: CompanyUpdate, current_user: dict = Depends(get_current_user)):
    """Update company (owner only)"""
    if current_user["type"] != "owner":
        raise HTTPException(status_code=403, detail="Access denied")
    
    existing_company = await db.find_one("companies", {"id": company_id})
    if not existing_company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    update_data = {k: v for k, v in company.dict().items() if v is not None}
    if update_data:
        await db.update_one("companies", {"id": company_id}, update_data)
    
    # Clear cache
    cache.clear()
    
    updated_company = await db.find_one("companies", {"id": company_id})
    updated_company["created_at"] = parse_datetime(updated_company["created_at"])
    return updated_company

@api_router.delete("/companies/{company_id}")
async def delete_company(company_id: str, current_user: dict = Depends(get_current_user)):
    """Delete company (owner only)"""
    if current_user["type"] != "owner":
        raise HTTPException(status_code=403, detail="Access denied")
    
    deleted = await db.delete_one("companies", {"id": company_id})
    if not deleted:
        raise HTTPException(status_code=404, detail="Company not found")
    
    # Clear cache
    cache.clear()
    
    return {"message": "Company deleted successfully"}

# === AUTHENTICATION ROUTES ===

@api_router.get("/users", response_model=List[UserResponse])
@cached(duration=300)  # 5 minutes cache
async def get_users(current_user: dict = Depends(get_current_user)):
    """Get users (owner: all users, admin: users from their company) with cache"""
    if current_user["type"] == "owner":
        users = await db.find_many("users")
    elif current_user["type"] == "admin":
        # Admin can only see users from their company
        users = await db.find_many("users", {"company_id": current_user["company_id"]})
    else:
        raise HTTPException(status_code=403, detail="Access denied")
    
    user_responses = []
    for user in users:
        company_name = user.get("company_name")
        if user.get("company_id"):
            company = await db.find_one("companies", {"id": user["company_id"]})
            if company:
                company_name = company["name"]
        
        created_at = parse_datetime(user["created_at"]) if isinstance(user["created_at"], str) else user["created_at"]
        
        user_responses.append(UserResponse(
            id=user["id"],
            username=user["username"],
            type=user["type"],
            role=user["role"],
            company_id=user.get("company_id"),
            company_name=company_name,
            created_at=created_at
        ))
    
    return user_responses

@api_router.post("/users", response_model=UserResponse)
async def create_user(user: UserCreate, current_user: dict = Depends(get_current_user)):
    """Create new user (owner: any user, admin: users for their company only)"""
    if current_user["type"] == "owner":
        # Owner can create users for any company
        pass
    elif current_user["type"] == "admin":
        # Admin can only create users for their company
        if not user.company_id:
            user.company_id = current_user["company_id"]
        elif user.company_id != current_user["company_id"]:
            raise HTTPException(status_code=403, detail="Cannot create users for other companies")
        # Admin cannot create owner accounts
        if user.type == "owner":
            raise HTTPException(status_code=403, detail="Cannot create owner accounts")
    else:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Check if username already exists
    existing_user = await db.find_one("users", {"username": user.username})
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    # Get company name if provided
    company_name = None
    if user.company_id:
        company = await db.find_one("companies", {"id": user.company_id})
        if company:
            company_name = company["name"]
    
    user_obj = User(
        username=user.username,
        password_hash=hash_password(user.password),
        type=user.type,
        role=user.type,
        company_id=user.company_id,
        company_name=company_name
    )
    
    await db.insert_one("users", user_obj.dict())
    
    # Clear cache
    cache.clear()
    
    return UserResponse(
        id=user_obj.id,
        username=user_obj.username,
        type=user_obj.type,
        role=user_obj.role,
        company_id=user_obj.company_id,
        company_name=company_name,
        created_at=user_obj.created_at
    )

# === EMPLOYEE ROUTES ===

@api_router.get("/employees", response_model=List[Employee])
@cached(duration=300)  # 5 minutes cache
async def get_employees(current_user: dict = Depends(get_current_user)):
    """Get employees (admin/user for their company, owner for all) with cache"""
    if current_user["type"] == "owner":
        employees = await db.find_many("employees")
    else:
        employees = await db.find_many("employees", {"company_id": current_user["company_id"]})
    
    # Parse datetime fields
    for employee in employees:
        employee["created_at"] = parse_datetime(employee["created_at"])
    
    return employees

@api_router.post("/employees", response_model=Employee)
async def create_employee(employee: EmployeeCreate, current_user: dict = Depends(get_current_user)):
    """Create new employee (admin only)"""
    if current_user["type"] not in ["owner", "admin"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Generate QR code
    qr_code = f"QR-EMP-{str(uuid.uuid4())[:8].upper()}"
    
    employee_obj = Employee(
        name=employee.name,
        qr_code=qr_code,
        company_id=employee.company_id
    )
    
    await db.insert_one("employees", employee_obj.dict())
    
    # Clear cache
    cache.clear()
    
    return employee_obj

@api_router.get("/employees/{employee_id}/qr", response_model=QRResponse)
async def generate_employee_qr(employee_id: str, current_user: dict = Depends(get_current_user)):
    """Generate QR code for employee (admin only)"""
    if current_user["type"] not in ["owner", "admin"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    employee = await db.find_one("employees", {"id": employee_id})
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    qr_image = generate_qr_code(employee["qr_code"])
    
    return QRResponse(
        qr_code_data=employee["qr_code"],
        qr_code_image=qr_image
    )

# === TIME ENTRY ROUTES ===

@api_router.get("/time-entries", response_model=List[TimeEntry])
@cached(duration=180)  # 3 minutes cache (shorter because data changes)
async def get_time_entries(current_user: dict = Depends(get_current_user)):
    """Get time entries (admin/user for their company, owner for all) with cache"""
    if current_user["type"] == "owner":
        time_entries = await db.find_many("time_entries")
    else:
        # Get employees from user's company first
        employees = await db.find_many("employees", {"company_id": current_user["company_id"]})
        employee_ids = [emp["id"] for emp in employees]
        time_entries = await db.find_time_entries_by_employee_ids(employee_ids)
    
    # Parse datetime fields
    for entry in time_entries:
        entry["check_in"] = parse_datetime(entry["check_in"])
        if entry["check_out"]:
            entry["check_out"] = parse_datetime(entry["check_out"])
        entry["created_at"] = parse_datetime(entry["created_at"])
    
    return time_entries

@api_router.post("/qr-scan", response_model=QRScanResponse)
async def process_qr_scan(request: QRScanRequest, current_user: dict = Depends(get_current_user)):
    """Process QR code scan for employee check-in/check-out"""
    try:
        # Find employee by QR code
        employee = await db.find_one("employees", {"qr_code": request.qr_code})
        
        if not employee:
            return QRScanResponse(
                success=False,
                message="QR kod nie istnieje"
            )
        
        # Check if employee belongs to the same company as the user
        if str(employee.get("company_id")) != str(current_user.get("company_id")):
            return QRScanResponse(
                success=False,
                message="QR kod nie należy do Twojej firmy"
            )
        
        # Check if employee is active
        if not employee.get("is_active", True):
            return QRScanResponse(
                success=False,
                message="Pracownik jest nieaktywny"
            )
        
        # Get today's date
        today = datetime.utcnow().strftime("%Y-%m-%d")
        
        # Find the last time entry for this employee today
        last_entry = await db.find_last_time_entry(employee["id"], today)
        
        now = datetime.utcnow()
        
        # Determine if this is check-in or check-out
        if not last_entry or last_entry.get("check_out"):
            # This is check-in
            action = "check_in"
            action_text = "Rozpoczęto pracę"
            
            # Create new time entry
            time_entry = TimeEntry(
                employee_id=employee["id"],
                check_in=now,
                check_out=None,
                date=today,
                total_hours=None
            )
            
            await db.insert_one("time_entries", time_entry.dict())
            
        else:
            # This is check-out
            action = "check_out"
            action_text = "Zakończono pracę"
            
            # Update existing time entry
            check_in = parse_datetime(last_entry["check_in"])
            
            delta = now - check_in
            total_hours = delta.total_seconds() / 3600
            
            await db.update_one(
                "time_entries",
                {"id": last_entry["id"]},
                {
                    "check_out": now,
                    "total_hours": total_hours
                }
            )
        
        # Clear cache after scan
        cache.clear()
        
        return QRScanResponse(
            success=True,
            action=action,
            employee_name=employee["name"],
            time=now.strftime("%Y-%m-%d %H:%M:%S"),
            message=f"{action_text} dla {employee['name']}",
            cooldown_seconds=5
        )
        
    except Exception as e:
        logger.error(f"Error processing QR scan: {str(e)}")
        return QRScanResponse(
            success=False,
            message="Błąd podczas przetwarzania skanowania QR"
        )

# === ORIGINAL ROUTES (for compatibility) ===

@api_router.get("/")
async def root():
    return {"message": "Hello World"}

@api_router.post("/status", response_model=StatusCheck)
async def create_status_check(input: StatusCheckCreate):
    status_dict = input.dict()
    status_obj = StatusCheck(**status_dict)
    await db.insert_one("status_checks", status_obj.dict())
    return status_obj

@api_router.get("/status", response_model=List[StatusCheck])
async def get_status_checks():
    status_checks = await db.find_many("status_checks")
    
    # Parse datetime fields
    for check in status_checks:
        check["timestamp"] = parse_datetime(check["timestamp"])
    
    return [StatusCheck(**status_check) for status_check in status_checks]

# Include the router in the main app
app.include_router(api_router)

# CORS Configuration
cors_origins = os.environ.get('CORS_ORIGINS', '["*"]')
if cors_origins.startswith('['):
    cors_origins = json.loads(cors_origins)
else:
    cors_origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=cors_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Clear cache periodically
async def clear_cache_periodically():
    while True:
        await asyncio.sleep(3600)  # Every hour
        cache.clear()
        logger.info("Cache cleared")

@app.on_event("startup")
async def startup_event():
    await db.init_db()
    await init_default_data()
    asyncio.create_task(clear_cache_periodically())
    logger.info("Application started, default data initialized, and cache cleaner scheduled")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Application shutting down")