#!/usr/bin/env python3
"""
Database module for TimeTracker Pro - SQLite support
Compatible with home.pl CGI hosting
"""
import sqlite3
import json
from typing import List, Dict, Optional, Any
from datetime import datetime
import uuid
import os

class Database:
    def __init__(self, db_path: str = "timetracker_pro.db"):
        self.db_path = db_path
        
    def init_db(self):
        """Initialize database tables"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Users table
            cursor.execute("""
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
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS companies (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
            """)
            
            # Employees table
            cursor.execute("""
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
            cursor.execute("""
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
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS status_checks (
                    id TEXT PRIMARY KEY,
                    client_name TEXT NOT NULL,
                    timestamp TEXT NOT NULL
                )
            """)
            
            conn.commit()
            
    def insert_one(self, table: str, data: Dict[str, Any]) -> bool:
        """Insert a document into a table"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Convert datetime objects to ISO strings
            for key, value in data.items():
                if isinstance(value, datetime):
                    data[key] = value.isoformat()
            
            columns = ', '.join(data.keys())
            placeholders = ', '.join(['?' for _ in data])
            values = list(data.values())
            
            cursor.execute(f"INSERT INTO {table} ({columns}) VALUES ({placeholders})", values)
            conn.commit()
            return True
            
    def insert_many(self, table: str, data_list: List[Dict[str, Any]]) -> bool:
        """Insert multiple documents into a table"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            for data in data_list:
                # Convert datetime objects to ISO strings
                for key, value in data.items():
                    if isinstance(value, datetime):
                        data[key] = value.isoformat()
                
                columns = ', '.join(data.keys())
                placeholders = ', '.join(['?' for _ in data])
                values = list(data.values())
                
                cursor.execute(f"INSERT INTO {table} ({columns}) VALUES ({placeholders})", values)
            
            conn.commit()
            return True
    
    def find_one(self, table: str, filter_dict: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
        """Find a single document"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            if filter_dict:
                where_clause = ' AND '.join([f"{k} = ?" for k in filter_dict.keys()])
                values = list(filter_dict.values())
                cursor.execute(f"SELECT * FROM {table} WHERE {where_clause}", values)
            else:
                cursor.execute(f"SELECT * FROM {table}")
            
            row = cursor.fetchone()
            if row:
                return dict(row)
            return None
    
    def find_many(self, table: str, filter_dict: Dict[str, Any] = None, sort_by: str = None, limit: int = 1000) -> List[Dict[str, Any]]:
        """Find multiple documents"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            query = f"SELECT * FROM {table}"
            values = []
            
            if filter_dict:
                where_clause = ' AND '.join([f"{k} = ?" for k in filter_dict.keys()])
                query += f" WHERE {where_clause}"
                values = list(filter_dict.values())
            
            if sort_by:
                query += f" ORDER BY {sort_by}"
                
            query += f" LIMIT {limit}"
            
            cursor.execute(query, values)
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    
    def update_one(self, table: str, filter_dict: Dict[str, Any], update_dict: Dict[str, Any]) -> bool:
        """Update a single document"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Convert datetime objects to ISO strings
            for key, value in update_dict.items():
                if isinstance(value, datetime):
                    update_dict[key] = value.isoformat()
            
            set_clause = ', '.join([f"{k} = ?" for k in update_dict.keys()])
            where_clause = ' AND '.join([f"{k} = ?" for k in filter_dict.keys()])
            
            values = list(update_dict.values()) + list(filter_dict.values())
            
            cursor.execute(f"UPDATE {table} SET {set_clause} WHERE {where_clause}", values)
            conn.commit()
            return cursor.rowcount > 0
    
    def delete_one(self, table: str, filter_dict: Dict[str, Any]) -> bool:
        """Delete a single document"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            where_clause = ' AND '.join([f"{k} = ?" for k in filter_dict.keys()])
            values = list(filter_dict.values())
            
            cursor.execute(f"DELETE FROM {table} WHERE {where_clause}", values)
            conn.commit()
            return cursor.rowcount > 0
    
    def find_time_entries_by_employee_ids(self, employee_ids: List[str]) -> List[Dict[str, Any]]:
        """Find time entries for multiple employees"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            placeholders = ', '.join(['?' for _ in employee_ids])
            cursor.execute(f"SELECT * FROM time_entries WHERE employee_id IN ({placeholders})", employee_ids)
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    
    def find_time_entries_by_date_range(self, employee_id: str, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """Find time entries by date range"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute(
                "SELECT * FROM time_entries WHERE employee_id = ? AND date >= ? AND date < ?",
                (employee_id, start_date, end_date)
            )
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    
    def find_last_time_entry(self, employee_id: str, date: str) -> Optional[Dict[str, Any]]:
        """Find the last time entry for an employee on a specific date"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute(
                "SELECT * FROM time_entries WHERE employee_id = ? AND date = ? ORDER BY check_in DESC LIMIT 1",
                (employee_id, date)
            )
            row = cursor.fetchone()
            if row:
                return dict(row)
            return None