import aiosqlite
import os
import json
from typing import List, Dict, Optional, Any
from datetime import datetime
import uuid

class Database:
    def __init__(self, db_path: str):
        self.db_path = db_path
        
    async def init_db(self):
        """Initialize database tables"""
        async with aiosqlite.connect(self.db_path) as db:
            # Users table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id TEXT PRIMARY KEY,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    type TEXT NOT NULL,
                    role TEXT NOT NULL,
                    company_id TEXT,
                    company_name TEXT,
                    created_at TEXT NOT NULL
                )
            """)
            
            # Companies table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS companies (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
            """)
            
            # Employees table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS employees (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    qr_code TEXT UNIQUE NOT NULL,
                    company_id TEXT NOT NULL,
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TEXT NOT NULL
                )
            """)
            
            # Time entries table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS time_entries (
                    id TEXT PRIMARY KEY,
                    employee_id TEXT NOT NULL,
                    check_in TEXT NOT NULL,
                    check_out TEXT,
                    date TEXT NOT NULL,
                    total_hours REAL,
                    created_at TEXT NOT NULL
                )
            """)
            
            # Status checks table (for compatibility)
            await db.execute("""
                CREATE TABLE IF NOT EXISTS status_checks (
                    id TEXT PRIMARY KEY,
                    client_name TEXT NOT NULL,
                    timestamp TEXT NOT NULL
                )
            """)
            
            await db.commit()
            
    async def insert_one(self, table: str, data: Dict[str, Any]) -> bool:
        """Insert a document into a table"""
        async with aiosqlite.connect(self.db_path) as db:
            # Convert datetime objects to ISO strings
            for key, value in data.items():
                if isinstance(value, datetime):
                    data[key] = value.isoformat()
            
            columns = ', '.join(data.keys())
            placeholders = ', '.join(['?' for _ in data])
            values = list(data.values())
            
            await db.execute(f"INSERT INTO {table} ({columns}) VALUES ({placeholders})", values)
            await db.commit()
            return True
            
    async def insert_many(self, table: str, data_list: List[Dict[str, Any]]) -> bool:
        """Insert multiple documents into a table"""
        async with aiosqlite.connect(self.db_path) as db:
            for data in data_list:
                # Convert datetime objects to ISO strings
                for key, value in data.items():
                    if isinstance(value, datetime):
                        data[key] = value.isoformat()
                
                columns = ', '.join(data.keys())
                placeholders = ', '.join(['?' for _ in data])
                values = list(data.values())
                
                await db.execute(f"INSERT INTO {table} ({columns}) VALUES ({placeholders})", values)
            await db.commit()
            return True
    
    async def find_one(self, table: str, filter_dict: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
        """Find a single document"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            
            if filter_dict:
                where_clause = ' AND '.join([f"{k} = ?" for k in filter_dict.keys()])
                values = list(filter_dict.values())
                cursor = await db.execute(f"SELECT * FROM {table} WHERE {where_clause}", values)
            else:
                cursor = await db.execute(f"SELECT * FROM {table}")
            
            row = await cursor.fetchone()
            if row:
                return dict(row)
            return None
    
    async def find_many(self, table: str, filter_dict: Dict[str, Any] = None, sort_by: str = None, limit: int = 1000) -> List[Dict[str, Any]]:
        """Find multiple documents"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            
            query = f"SELECT * FROM {table}"
            values = []
            
            if filter_dict:
                where_clause = ' AND '.join([f"{k} = ?" for k in filter_dict.keys()])
                query += f" WHERE {where_clause}"
                values = list(filter_dict.values())
            
            if sort_by:
                query += f" ORDER BY {sort_by}"
                
            query += f" LIMIT {limit}"
            
            cursor = await db.execute(query, values)
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]
    
    async def update_one(self, table: str, filter_dict: Dict[str, Any], update_dict: Dict[str, Any]) -> bool:
        """Update a single document"""
        async with aiosqlite.connect(self.db_path) as db:
            # Convert datetime objects to ISO strings
            for key, value in update_dict.items():
                if isinstance(value, datetime):
                    update_dict[key] = value.isoformat()
            
            set_clause = ', '.join([f"{k} = ?" for k in update_dict.keys()])
            where_clause = ' AND '.join([f"{k} = ?" for k in filter_dict.keys()])
            
            values = list(update_dict.values()) + list(filter_dict.values())
            
            await db.execute(f"UPDATE {table} SET {set_clause} WHERE {where_clause}", values)
            await db.commit()
            return True
    
    async def delete_one(self, table: str, filter_dict: Dict[str, Any]) -> bool:
        """Delete a single document"""
        async with aiosqlite.connect(self.db_path) as db:
            where_clause = ' AND '.join([f"{k} = ?" for k in filter_dict.keys()])
            values = list(filter_dict.values())
            
            cursor = await db.execute(f"DELETE FROM {table} WHERE {where_clause}", values)
            await db.commit()
            return cursor.rowcount > 0
    
    async def find_time_entries_by_employee_ids(self, employee_ids: List[str]) -> List[Dict[str, Any]]:
        """Find time entries for multiple employees"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            
            placeholders = ', '.join(['?' for _ in employee_ids])
            cursor = await db.execute(f"SELECT * FROM time_entries WHERE employee_id IN ({placeholders})", employee_ids)
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]
    
    async def find_time_entries_by_date_range(self, employee_id: str, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """Find time entries by date range"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            
            cursor = await db.execute(
                "SELECT * FROM time_entries WHERE employee_id = ? AND date >= ? AND date < ?",
                (employee_id, start_date, end_date)
            )
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]
    
    async def find_last_time_entry(self, employee_id: str, date: str) -> Optional[Dict[str, Any]]:
        """Find the last time entry for an employee on a specific date"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            
            cursor = await db.execute(
                "SELECT * FROM time_entries WHERE employee_id = ? AND date = ? ORDER BY check_in DESC LIMIT 1",
                (employee_id, date)
            )
            row = await cursor.fetchone()
            if row:
                return dict(row)
            return None