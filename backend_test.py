#!/usr/bin/env python3
"""
Comprehensive Backend API Testing for TimeTracker Pro
Tests all API endpoints with proper authentication and error handling
"""

import requests
import sys
import json
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

class TimeTrackerAPITester:
    def __init__(self, base_url: str = "http://localhost:8001/api"):
        self.base_url = base_url
        self.tokens = {}  # Store tokens for different users
        self.test_data = {}  # Store created test data
        self.tests_run = 0
        self.tests_passed = 0
        self.session = requests.Session()
        
        print(f"🚀 Starting TimeTracker Pro API Tests")
        print(f"📡 Base URL: {self.base_url}")
        print("=" * 60)

    def log_test(self, name: str, success: bool, details: str = ""):
        """Log test results"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name}")
        else:
            print(f"❌ {name}")
        
        if details:
            print(f"   {details}")

    def make_request(self, method: str, endpoint: str, data: Optional[Dict] = None, 
                    token: Optional[str] = None, expected_status: int = 200) -> tuple[bool, Dict]:
        """Make HTTP request with proper error handling"""
        url = f"{self.base_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}
        
        if token:
            headers['Authorization'] = f'Bearer {token}'
        
        try:
            if method == 'GET':
                response = self.session.get(url, headers=headers)
            elif method == 'POST':
                response = self.session.post(url, json=data, headers=headers)
            elif method == 'PUT':
                response = self.session.put(url, json=data, headers=headers)
            elif method == 'DELETE':
                response = self.session.delete(url, headers=headers)
            else:
                return False, {"error": f"Unsupported method: {method}"}
            
            success = response.status_code == expected_status
            
            try:
                response_data = response.json()
            except:
                response_data = {"raw_response": response.text, "status_code": response.status_code}
            
            if not success:
                response_data["status_code"] = response.status_code
                
            return success, response_data
            
        except Exception as e:
            return False, {"error": str(e)}

    def test_authentication(self):
        """Test authentication endpoints"""
        print("\n🔐 Testing Authentication...")
        
        # Test valid login for each user type
        test_users = [
            ("owner", "owner123", "owner"),
            ("admin", "admin123", "admin"), 
            ("user", "user123", "user")
        ]
        
        for username, password, user_type in test_users:
            success, response = self.make_request(
                'POST', 'auth/login',
                data={"username": username, "password": password}
            )
            
            if success and 'access_token' in response:
                self.tokens[user_type] = response['access_token']
                user_info = response.get('user', {})
                self.log_test(
                    f"Login {username}",
                    True,
                    f"Token received, User type: {user_info.get('type', 'unknown')}"
                )
            else:
                self.log_test(
                    f"Login {username}",
                    False,
                    f"Response: {response}"
                )
        
        # Test invalid login
        success, response = self.make_request(
            'POST', 'auth/login',
            data={"username": "invalid", "password": "invalid"},
            expected_status=401
        )
        self.log_test("Invalid login", success, "Should return 401")

    def test_companies(self):
        """Test company management endpoints"""
        print("\n🏢 Testing Company Management...")
        
        if 'owner' not in self.tokens:
            self.log_test("Company tests", False, "Owner token not available")
            return
        
        owner_token = self.tokens['owner']
        
        # Get companies
        success, response = self.make_request('GET', 'companies', token=owner_token)
        self.log_test("Get companies", success, f"Found {len(response) if success else 0} companies")
        
        # Create company
        company_data = {"name": f"Test Company {datetime.now().strftime('%H%M%S')}"}
        success, response = self.make_request('POST', 'companies', data=company_data, token=owner_token)
        
        if success:
            self.test_data['company_id'] = response['id']
            self.log_test("Create company", True, f"Created company: {response['name']}")
        else:
            self.log_test("Create company", False, f"Response: {response}")
        
        # Test admin access (should be denied)
        if 'admin' in self.tokens:
            success, response = self.make_request('GET', 'companies', token=self.tokens['admin'], expected_status=403)
            self.log_test("Admin company access", success, "Should be denied (403)")

    def test_users(self):
        """Test user management endpoints"""
        print("\n👥 Testing User Management...")
        
        if 'owner' not in self.tokens:
            self.log_test("User tests", False, "Owner token not available")
            return
        
        owner_token = self.tokens['owner']
        
        # Get users
        success, response = self.make_request('GET', 'users', token=owner_token)
        self.log_test("Get users", success, f"Found {len(response) if success else 0} users")
        
        # Create user
        user_data = {
            "username": f"testuser_{datetime.now().strftime('%H%M%S')}",
            "password": "TestPass123!",
            "type": "user",
            "company_id": "1"
        }
        success, response = self.make_request('POST', 'users', data=user_data, token=owner_token)
        
        if success:
            self.test_data['user_id'] = response['id']
            self.log_test("Create user", True, f"Created user: {response['username']}")
        else:
            self.log_test("Create user", False, f"Response: {response}")
        
        # Test admin user access (should only see company users)
        if 'admin' in self.tokens:
            success, response = self.make_request('GET', 'users', token=self.tokens['admin'])
            self.log_test("Admin get users", success, f"Admin sees {len(response) if success else 0} users")

    def test_employees(self):
        """Test employee management endpoints"""
        print("\n👷 Testing Employee Management...")
        
        if 'admin' not in self.tokens:
            self.log_test("Employee tests", False, "Admin token not available")
            return
        
        admin_token = self.tokens['admin']
        
        # Get employees
        success, response = self.make_request('GET', 'employees', token=admin_token)
        self.log_test("Get employees", success, f"Found {len(response) if success else 0} employees")
        
        # Create employee
        employee_data = {
            "name": f"Test Employee {datetime.now().strftime('%H%M%S')}",
            "company_id": "1"
        }
        success, response = self.make_request('POST', 'employees', data=employee_data, token=admin_token)
        
        if success:
            self.test_data['employee_id'] = response['id']
            self.test_data['employee_qr'] = response['qr_code']
            self.log_test("Create employee", True, f"Created: {response['name']}, QR: {response['qr_code']}")
        else:
            self.log_test("Create employee", False, f"Response: {response}")
        
        # Test QR code generation
        if 'employee_id' in self.test_data:
            success, response = self.make_request('GET', f"employees/{self.test_data['employee_id']}/qr", token=admin_token)
            self.log_test("Generate QR code", success, "QR code generated" if success else f"Error: {response}")

    def test_time_entries(self):
        """Test time entry management endpoints"""
        print("\n⏰ Testing Time Entry Management...")
        
        if 'admin' not in self.tokens or 'employee_id' not in self.test_data:
            self.log_test("Time entry tests", False, "Admin token or employee not available")
            return
        
        admin_token = self.tokens['admin']
        
        # Get time entries
        success, response = self.make_request('GET', 'time-entries', token=admin_token)
        self.log_test("Get time entries", success, f"Found {len(response) if success else 0} entries")
        
        # Create time entry
        now = datetime.utcnow()
        time_entry_data = {
            "employee_id": self.test_data['employee_id'],
            "check_in": now.isoformat(),
            "check_out": (now + timedelta(hours=8)).isoformat()
        }
        success, response = self.make_request('POST', 'time-entries', data=time_entry_data, token=admin_token)
        
        if success:
            self.test_data['time_entry_id'] = response['id']
            self.log_test("Create time entry", True, f"Entry created with {response.get('total_hours', 0):.1f} hours")
        else:
            self.log_test("Create time entry", False, f"Response: {response}")

    def test_qr_scanning(self):
        """Test QR code scanning functionality"""
        print("\n📱 Testing QR Code Scanning...")
        
        if 'admin' not in self.tokens or 'employee_qr' not in self.test_data:
            self.log_test("QR scan tests", False, "Admin token or employee QR not available")
            return
        
        admin_token = self.tokens['admin']
        
        # Test QR scan
        qr_scan_data = {
            "qr_code": self.test_data['employee_qr'],
            "user_id": "admin_user_id"
        }
        success, response = self.make_request('POST', 'qr-scan', data=qr_scan_data, token=admin_token)
        
        if success:
            action = response.get('action', 'unknown')
            employee_name = response.get('employee_name', 'unknown')
            self.log_test("QR scan", True, f"Action: {action}, Employee: {employee_name}")
        else:
            self.log_test("QR scan", False, f"Response: {response}")

    def test_employee_summaries(self):
        """Test employee summary and reporting endpoints"""
        print("\n📊 Testing Employee Summaries...")
        
        if 'admin' not in self.tokens:
            self.log_test("Summary tests", False, "Admin token not available")
            return
        
        admin_token = self.tokens['admin']
        
        # Get employee summary
        success, response = self.make_request('GET', 'employee-summary', token=admin_token)
        self.log_test("Employee summary", success, f"Found {len(response) if success else 0} employee summaries")
        
        # Test employee months (if we have an employee)
        if 'employee_id' in self.test_data:
            success, response = self.make_request('GET', f"employee-months/{self.test_data['employee_id']}", token=admin_token)
            self.log_test("Employee months", success, f"Found {len(response) if success else 0} months")

    def test_unauthorized_access(self):
        """Test unauthorized access scenarios"""
        print("\n🚫 Testing Unauthorized Access...")
        
        # Test without token
        success, response = self.make_request('GET', 'employees', expected_status=403)
        self.log_test("No token access", success, "Should be denied")
        
        # Test with invalid token
        success, response = self.make_request('GET', 'employees', token="invalid_token", expected_status=401)
        self.log_test("Invalid token access", success, "Should be denied")
        
        # Test user accessing admin endpoints
        if 'user' in self.tokens:
            success, response = self.make_request('GET', 'companies', token=self.tokens['user'], expected_status=403)
            self.log_test("User accessing companies", success, "Should be denied")

    def test_basic_endpoints(self):
        """Test basic endpoints"""
        print("\n🔧 Testing Basic Endpoints...")
        
        # Test root endpoint
        success, response = self.make_request('GET', '')
        self.log_test("Root endpoint", success, response.get('message', ''))
        
        # Test status endpoints
        status_data = {"client_name": "test_client"}
        success, response = self.make_request('POST', 'status', data=status_data)
        self.log_test("Create status", success, "Status created" if success else f"Error: {response}")
        
        success, response = self.make_request('GET', 'status')
        self.log_test("Get status", success, f"Found {len(response) if success else 0} status entries")

    def run_all_tests(self):
        """Run all test suites"""
        try:
            self.test_basic_endpoints()
            self.test_authentication()
            self.test_companies()
            self.test_users()
            self.test_employees()
            self.test_time_entries()
            self.test_qr_scanning()
            self.test_employee_summaries()
            self.test_unauthorized_access()
            
        except Exception as e:
            print(f"❌ Test suite failed with error: {str(e)}")
        
        finally:
            self.print_summary()

    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        print(f"Total tests run: {self.tests_run}")
        print(f"Tests passed: {self.tests_passed}")
        print(f"Tests failed: {self.tests_run - self.tests_passed}")
        print(f"Success rate: {(self.tests_passed/self.tests_run*100):.1f}%" if self.tests_run > 0 else "No tests run")
        
        if self.tests_passed == self.tests_run:
            print("🎉 All tests passed!")
            return 0
        else:
            print("⚠️  Some tests failed!")
            return 1

def main():
    """Main test runner"""
    tester = TimeTrackerAPITester()
    return tester.run_all_tests()

if __name__ == "__main__":
    sys.exit(main())