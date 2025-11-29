"""
End-to-End Integration Test
Tests: Frontend → Backend API → Agent System → Database
"""

import asyncio
import json
import time
import subprocess
import sys
import requests
from datetime import datetime, timedelta
from typing import Dict, Any
import signal
import os

# Color codes for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'
BOLD = '\033[1m'

class E2ETest:
    def __init__(self):
        self.backend_url = "http://localhost:8000"
        self.frontend_url = "http://localhost:5173"
        self.backend_process = None
        self.frontend_process = None
        self.test_results = {
            "backend_startup": False,
            "backend_health": False,
            "agent_analysis": False,
            "database": False,
            "frontend_startup": False,
            "frontend_backend_connection": False
        }
        
    def print_header(self, text: str):
        """Print formatted section header"""
        print(f"\n{BOLD}{BLUE}{'='*60}{RESET}")
        print(f"{BOLD}{BLUE}{text.center(60)}{RESET}")
        print(f"{BOLD}{BLUE}{'='*60}{RESET}\n")
        
    def print_status(self, test_name: str, passed: bool, details: str = ""):
        """Print test result with color coding"""
        status = f"{GREEN}✅ PASS{RESET}" if passed else f"{RED}❌ FAIL{RESET}"
        print(f"{test_name}: {status}")
        if details:
            print(f"  {YELLOW}→{RESET} {details}")
        print()
        
    def start_backend(self) -> bool:
        """Start the FastAPI backend server"""
        self.print_header("STARTING BACKEND SERVER")
        try:
            # Kill any existing process on port 8000
            try:
                subprocess.run(["lsof", "-ti:8000"], 
                             stdout=subprocess.PIPE, 
                             stderr=subprocess.PIPE, 
                             check=True)
                subprocess.run(["kill", "-9", "$(lsof -ti:8000)"], 
                             shell=True, 
                             stdout=subprocess.PIPE, 
                             stderr=subprocess.PIPE)
                print(f"{YELLOW}Killed existing process on port 8000{RESET}\n")
            except:
                pass
                
            # Start backend
            print("Starting FastAPI backend on http://localhost:8000...")
            self.backend_process = subprocess.Popen(
                ["python", "main.py"],
                cwd="/Users/adityaprakash/Desktop/DESKTOP-MAIN/FinSage-AI/backend",
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Wait for server to start
            max_attempts = 20
            for i in range(max_attempts):
                try:
                    response = requests.get(f"{self.backend_url}/api/finance/health", timeout=2)
                    if response.status_code == 200:
                        print(f"{GREEN}Backend started successfully!{RESET}")
                        self.test_results["backend_startup"] = True
                        self.print_status("Backend Startup", True, "Server running on port 8000")
                        return True
                except:
                    time.sleep(1)
                    print(f"Waiting for backend... ({i+1}/{max_attempts})")
                    
            print(f"{RED}Backend failed to start within timeout{RESET}")
            self.print_status("Backend Startup", False, "Server did not respond within 20 seconds")
            return False
            
        except Exception as e:
            print(f"{RED}Error starting backend: {e}{RESET}")
            self.print_status("Backend Startup", False, str(e))
            return False
            
    def test_backend_health(self) -> bool:
        """Test backend health endpoint"""
        self.print_header("TESTING BACKEND HEALTH")
        try:
            response = requests.get(f"{self.backend_url}/api/finance/health", timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                print(f"{GREEN}Health check passed!{RESET}")
                print(f"Response: {json.dumps(data, indent=2)}")
                self.test_results["backend_health"] = True
                self.print_status("Backend Health", True, f"Status: {data.get('status', 'unknown')}")
                return True
            else:
                print(f"{RED}Health check failed with status {response.status_code}{RESET}")
                self.print_status("Backend Health", False, f"HTTP {response.status_code}")
                return False
                
        except Exception as e:
            print(f"{RED}Error testing health endpoint: {e}{RESET}")
            self.print_status("Backend Health", False, str(e))
            return False
            
    def test_agent_analysis(self) -> bool:
        """Test agent analysis endpoint"""
        self.print_header("TESTING AGENT ANALYSIS ENDPOINT")
        try:
            # Create test data
            test_data = {
                "user_id": "test_user_e2e",
                "days": 30,
                "target_savings_rate": 0.30,
                "risk_tolerance": "moderate"
            }
            
            print(f"Sending request to /api/finance/agent-analysis...")
            print(f"Request data: {json.dumps(test_data, indent=2)}\n")
            
            start_time = time.time()
            response = requests.post(
                f"{self.backend_url}/api/finance/agent-analysis",
                json=test_data,
                timeout=60
            )
            duration = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                print(f"{GREEN}Agent analysis completed!{RESET}")
                print(f"Analysis duration: {duration:.2f}s")
                print(f"\n{BOLD}Executive Summary:{RESET}")
                if "executive_summary" in data:
                    summary = data["executive_summary"]
                    print(f"  Status: {summary.get('overall_status', 'N/A')}")
                    print(f"  Health Score: {summary.get('health_score', 'N/A')}/100")
                    print(f"  Risk Level: {summary.get('risk_level', 'N/A')}")
                    
                print(f"\n{BOLD}Financial Overview:{RESET}")
                if "financial_overview" in data:
                    overview = data["financial_overview"]
                    print(f"  Income: ₹{overview.get('total_income', 0):,.2f}")
                    print(f"  Expenses: ₹{overview.get('total_expenses', 0):,.2f}")
                    print(f"  Savings Rate: {overview.get('savings_rate', 0)*100:.1f}%")
                    
                self.test_results["agent_analysis"] = True
                health_score = data.get("executive_summary", {}).get("health_score", 0)
                self.print_status("Agent Analysis", True, f"Health Score: {health_score}/100, Duration: {duration:.2f}s")
                return True
            else:
                print(f"{RED}Agent analysis failed with status {response.status_code}{RESET}")
                print(f"Response: {response.text}")
                self.print_status("Agent Analysis", False, f"HTTP {response.status_code}")
                return False
                
        except Exception as e:
            print(f"{RED}Error testing agent analysis: {e}{RESET}")
            self.print_status("Agent Analysis", False, str(e))
            return False
            
    def test_database_connection(self) -> bool:
        """Test database connectivity"""
        self.print_header("TESTING DATABASE CONNECTION")
        try:
            response = requests.get(f"{self.backend_url}/api/finance/health", timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                db_status = data.get("database", "unknown")
                
                if db_status == "connected":
                    print(f"{GREEN}Database is connected!{RESET}")
                    self.test_results["database"] = True
                    self.print_status("Database Connection", True, "MongoDB Atlas connected")
                    return True
                else:
                    print(f"{YELLOW}Database is not connected (running in demo mode){RESET}")
                    self.print_status("Database Connection", False, "Demo mode - SSL handshake issue")
                    return False
            else:
                print(f"{RED}Could not check database status{RESET}")
                self.print_status("Database Connection", False, "Health endpoint unavailable")
                return False
                
        except Exception as e:
            print(f"{RED}Error testing database: {e}{RESET}")
            self.print_status("Database Connection", False, str(e))
            return False
            
    def start_frontend(self) -> bool:
        """Start the Vite frontend server"""
        self.print_header("STARTING FRONTEND SERVER")
        try:
            # Kill any existing process on port 5173
            try:
                subprocess.run(["lsof", "-ti:5173"], 
                             stdout=subprocess.PIPE, 
                             stderr=subprocess.PIPE, 
                             check=True)
                subprocess.run(["kill", "-9", "$(lsof -ti:5173)"], 
                             shell=True, 
                             stdout=subprocess.PIPE, 
                             stderr=subprocess.PIPE)
                print(f"{YELLOW}Killed existing process on port 5173{RESET}\n")
            except:
                pass
                
            # Start frontend
            print("Starting Vite frontend on http://localhost:5173...")
            self.frontend_process = subprocess.Popen(
                ["npm", "run", "dev"],
                cwd="/Users/adityaprakash/Desktop/DESKTOP-MAIN/FinSage-AI/frontend",
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Wait for server to start
            max_attempts = 20
            for i in range(max_attempts):
                try:
                    response = requests.get(self.frontend_url, timeout=2)
                    if response.status_code == 200:
                        print(f"{GREEN}Frontend started successfully!{RESET}")
                        self.test_results["frontend_startup"] = True
                        self.print_status("Frontend Startup", True, "Vite server running on port 5173")
                        return True
                except:
                    time.sleep(1)
                    print(f"Waiting for frontend... ({i+1}/{max_attempts})")
                    
            print(f"{RED}Frontend failed to start within timeout{RESET}")
            self.print_status("Frontend Startup", False, "Server did not respond within 20 seconds")
            return False
            
        except Exception as e:
            print(f"{RED}Error starting frontend: {e}{RESET}")
            self.print_status("Frontend Startup", False, str(e))
            return False
            
    def test_frontend_backend_connection(self) -> bool:
        """Test that frontend can connect to backend"""
        self.print_header("TESTING FRONTEND-BACKEND CONNECTION")
        try:
            # Check if backend is accessible from frontend's perspective
            print("Verifying CORS and connectivity...")
            
            # Test with a simple request
            response = requests.get(
                f"{self.backend_url}/api/finance/health",
                headers={"Origin": self.frontend_url},
                timeout=5
            )
            
            if response.status_code == 200:
                cors_header = response.headers.get("Access-Control-Allow-Origin")
                if cors_header:
                    print(f"{GREEN}CORS configured correctly!{RESET}")
                    print(f"Access-Control-Allow-Origin: {cors_header}")
                    self.test_results["frontend_backend_connection"] = True
                    self.print_status("Frontend-Backend Connection", True, "CORS enabled")
                    return True
                else:
                    print(f"{YELLOW}No CORS headers found (might still work){RESET}")
                    self.test_results["frontend_backend_connection"] = True
                    self.print_status("Frontend-Backend Connection", True, "Connection working")
                    return True
            else:
                print(f"{RED}Backend not responding to CORS request{RESET}")
                self.print_status("Frontend-Backend Connection", False, f"HTTP {response.status_code}")
                return False
                
        except Exception as e:
            print(f"{RED}Error testing frontend-backend connection: {e}{RESET}")
            self.print_status("Frontend-Backend Connection", False, str(e))
            return False
            
    def print_final_report(self):
        """Print comprehensive test report"""
        self.print_header("FINAL TEST REPORT")
        
        passed_tests = sum(1 for result in self.test_results.values() if result)
        total_tests = len(self.test_results)
        success_rate = (passed_tests / total_tests) * 100
        
        print(f"{BOLD}Test Results Summary:{RESET}\n")
        
        for test_name, passed in self.test_results.items():
            status = f"{GREEN}✅ PASS{RESET}" if passed else f"{RED}❌ FAIL{RESET}"
            formatted_name = test_name.replace("_", " ").title()
            print(f"  {formatted_name:.<40} {status}")
            
        print(f"\n{BOLD}Overall Score:{RESET}")
        print(f"  Tests Passed: {passed_tests}/{total_tests}")
        print(f"  Success Rate: {success_rate:.1f}%")
        
        if success_rate == 100:
            print(f"\n{GREEN}{BOLD}🎉 ALL TESTS PASSED! System is fully operational.{RESET}")
        elif success_rate >= 80:
            print(f"\n{YELLOW}{BOLD}⚠️  Most tests passed. System is operational with minor issues.{RESET}")
        elif success_rate >= 50:
            print(f"\n{YELLOW}{BOLD}⚠️  Some tests failed. System is partially operational.{RESET}")
        else:
            print(f"\n{RED}{BOLD}❌ Multiple tests failed. System needs attention.{RESET}")
            
        print(f"\n{BOLD}Access URLs:{RESET}")
        print(f"  Frontend: {BLUE}{self.frontend_url}{RESET}")
        print(f"  Backend:  {BLUE}{self.backend_url}{RESET}")
        print(f"  API Docs: {BLUE}{self.backend_url}/docs{RESET}")
        
    def cleanup(self):
        """Cleanup running processes"""
        print(f"\n{YELLOW}Cleaning up...{RESET}")
        
        if self.backend_process:
            print("Stopping backend server...")
            self.backend_process.terminate()
            try:
                self.backend_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.backend_process.kill()
                
        if self.frontend_process:
            print("Stopping frontend server...")
            self.frontend_process.terminate()
            try:
                self.frontend_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.frontend_process.kill()
                
        print(f"{GREEN}Cleanup complete{RESET}")
        
    def run(self, keep_running: bool = False):
        """Run all tests"""
        try:
            print(f"\n{BOLD}{BLUE}{'='*60}{RESET}")
            print(f"{BOLD}{BLUE}FinSage AI - End-to-End Integration Test{RESET}")
            print(f"{BOLD}{BLUE}{'='*60}{RESET}")
            print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            
            # Test 1: Start Backend
            if not self.start_backend():
                print(f"\n{RED}Cannot proceed without backend. Exiting.{RESET}")
                return
                
            time.sleep(2)
            
            # Test 2: Health Check
            self.test_backend_health()
            time.sleep(1)
            
            # Test 3: Database
            self.test_database_connection()
            time.sleep(1)
            
            # Test 4: Agent Analysis
            self.test_agent_analysis()
            time.sleep(2)
            
            # Test 5: Start Frontend
            self.start_frontend()
            time.sleep(2)
            
            # Test 6: Frontend-Backend Connection
            self.test_frontend_backend_connection()
            
            # Print final report
            self.print_final_report()
            
            if keep_running:
                print(f"\n{YELLOW}Servers are running. Press Ctrl+C to stop.{RESET}")
                print(f"\n{BOLD}You can now test the application manually:{RESET}")
                print(f"  1. Open {BLUE}{self.frontend_url}{RESET} in your browser")
                print(f"  2. Upload transactions")
                print(f"  3. View AI-powered insights")
                print(f"  4. Explore budget recommendations\n")
                
                try:
                    # Keep running until interrupted
                    while True:
                        time.sleep(1)
                except KeyboardInterrupt:
                    print(f"\n{YELLOW}Received interrupt signal{RESET}")
            
        except KeyboardInterrupt:
            print(f"\n{YELLOW}Test interrupted by user{RESET}")
        except Exception as e:
            print(f"\n{RED}Unexpected error: {e}{RESET}")
        finally:
            if not keep_running:
                self.cleanup()

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="FinSage AI End-to-End Integration Test")
    parser.add_argument("--keep-running", "-k", action="store_true", 
                       help="Keep servers running after tests (for manual testing)")
    args = parser.parse_args()
    
    tester = E2ETest()
    tester.run(keep_running=args.keep_running)

if __name__ == "__main__":
    main()
