"""
Comprehensive API and Feature Test Suite
Tests all endpoints, agents, and backend functionality
"""

import requests
import json
import time
from datetime import datetime, timedelta
from typing import Dict, Any
import secrets

# Configuration
API_BASE_URL = "http://localhost:8000"
TEST_USER_EMAIL = f"test_{secrets.token_urlsafe(8)}@example.com"
TEST_USER_PASSWORD = "TestPassword123!"
TEST_USER_NAME = "Test User"

# Color codes
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'
BOLD = '\033[1m'

class APITester:
    def __init__(self):
        self.token = None
        self.user_id = None
        self.test_results = {
            "passed": 0,
            "failed": 0,
            "total": 0
        }
        
    def print_header(self, text: str):
        """Print formatted section header"""
        print(f"\n{BOLD}{BLUE}{'='*70}{RESET}")
        print(f"{BOLD}{BLUE}{text.center(70)}{RESET}")
        print(f"{BOLD}{BLUE}{'='*70}{RESET}\n")
        
    def print_test(self, name: str, passed: bool, details: str = ""):
        """Print test result"""
        status = f"{GREEN}✅ PASS{RESET}" if passed else f"{RED}❌ FAIL{RESET}"
        self.test_results["total"] += 1
        if passed:
            self.test_results["passed"] += 1
        else:
            self.test_results["failed"] += 1
            
        print(f"{name:.<50} {status}")
        if details:
            print(f"  {YELLOW}→{RESET} {details}")
            
    def test_health_check(self):
        """Test health check endpoint"""
        self.print_header("TESTING HEALTH CHECK")
        
        try:
            response = requests.get(f"{API_BASE_URL}/api/finance/health", timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                self.print_test("Health check endpoint", True, f"Status: {data.get('status')}")
                return True
            else:
                self.print_test("Health check endpoint", False, f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.print_test("Health check endpoint", False, str(e))
            return False
            
    def test_register(self):
        """Test user registration"""
        self.print_header("TESTING USER REGISTRATION")
        
        try:
            payload = {
                "name": TEST_USER_NAME,
                "email": TEST_USER_EMAIL,
                "password": TEST_USER_PASSWORD
            }
            
            response = requests.post(
                f"{API_BASE_URL}/api/auth/register",
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("token")
                self.user_id = data.get("user", {}).get("id")
                
                self.print_test("User registration", True, f"User ID: {self.user_id}")
                self.print_test("JWT token generated", bool(self.token), f"Token length: {len(self.token) if self.token else 0}")
                return True
            else:
                self.print_test("User registration", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.print_test("User registration", False, str(e))
            return False
            
    def test_login(self):
        """Test user login"""
        self.print_header("TESTING USER LOGIN")
        
        try:
            payload = {
                "email": TEST_USER_EMAIL,
                "password": TEST_USER_PASSWORD
            }
            
            response = requests.post(
                f"{API_BASE_URL}/api/auth/login",
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("token")
                
                self.print_test("User login", True, f"Email: {TEST_USER_EMAIL}")
                self.print_test("Token refresh", bool(self.token), "New token received")
                return True
            else:
                self.print_test("User login", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.print_test("User login", False, str(e))
            return False
            
    def test_profile_update(self):
        """Test profile update with onboarding data"""
        self.print_header("TESTING PROFILE UPDATE")
        
        try:
            payload = {
                "userId": self.user_id,
                "onboarding_completed": True,
                "work_type": "freelancer",
                "income_stability": "variable",
                "monthly_income": 75000,
                "monthly_expenses": 45000,
                "financial_goals": ["emergency_fund", "save_more", "invest"],
                "biggest_challenge": "irregular_income",
                "current_savings": "1_3_months",
                "budget_experience": "sometimes",
                "risk_tolerance": "moderate",
                "notification_preferences": "weekly"
            }
            
            headers = {"Authorization": f"Bearer {self.token}"}
            response = requests.put(
                f"{API_BASE_URL}/api/auth/profile",
                json=payload,
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.print_test("Profile update", True, "Onboarding data saved")
                self.print_test("Monthly income", data.get("user", {}).get("profile", {}).get("monthly_income") == 75000)
                self.print_test("Risk tolerance", data.get("user", {}).get("profile", {}).get("risk_tolerance") == "moderate")
                return True
            else:
                self.print_test("Profile update", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.print_test("Profile update", False, str(e))
            return False
            
    def test_create_transactions(self):
        """Test creating sample transactions"""
        self.print_header("TESTING TRANSACTION CREATION")
        
        try:
            # Create sample transactions
            transactions = [
                {"type": "income", "category": "salary", "amount": 75000, "description": "Freelance project payment", "days_ago": 5},
                {"type": "expense", "category": "rent", "amount": 15000, "description": "Monthly rent", "days_ago": 3},
                {"type": "expense", "category": "groceries", "amount": 5000, "description": "Supermarket", "days_ago": 2},
                {"type": "expense", "category": "utilities", "amount": 3000, "description": "Electricity & water", "days_ago": 4},
                {"type": "income", "category": "freelance", "amount": 25000, "description": "Client payment", "days_ago": 10},
                {"type": "expense", "category": "transportation", "amount": 2000, "description": "Uber rides", "days_ago": 1},
                {"type": "expense", "category": "food", "amount": 3500, "description": "Restaurants", "days_ago": 1},
                {"type": "expense", "category": "entertainment", "amount": 1500, "description": "Movie tickets", "days_ago": 6},
            ]
            
            headers = {"Authorization": f"Bearer {self.token}"}
            created_count = 0
            
            for txn in transactions:
                date = (datetime.utcnow() - timedelta(days=txn["days_ago"])).isoformat()
                payload = {
                    "user_id": self.user_id,
                    "amount": txn["amount"],
                    "type": txn["type"],
                    "category": txn["category"],
                    "description": txn["description"],
                    "date": date
                }
                
                # Note: This endpoint needs to be implemented in finance_routes.py
                response = requests.post(
                    f"{API_BASE_URL}/api/finance/transactions",
                    json=payload,
                    headers=headers,
                    timeout=10
                )
                
                if response.status_code in [200, 201]:
                    created_count += 1
            
            self.print_test("Transaction creation", created_count == len(transactions), 
                          f"Created {created_count}/{len(transactions)} transactions")
            return created_count > 0
        except Exception as e:
            self.print_test("Transaction creation", False, str(e))
            return False
            
    def test_get_transactions(self):
        """Test retrieving transactions"""
        self.print_header("TESTING TRANSACTION RETRIEVAL")
        
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            response = requests.get(
                f"{API_BASE_URL}/api/finance/transactions",
                params={"user_id": self.user_id, "days": 30},
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                transactions = data.get("transactions", [])
                self.print_test("Get transactions", True, f"Found {len(transactions)} transactions")
                
                if transactions:
                    total_income = sum(t["amount"] for t in transactions if t["type"] == "income")
                    total_expense = sum(t["amount"] for t in transactions if t["type"] == "expense")
                    self.print_test("Income calculation", total_income > 0, f"₹{total_income:,.2f}")
                    self.print_test("Expense calculation", total_expense > 0, f"₹{total_expense:,.2f}")
                    
                return True
            else:
                self.print_test("Get transactions", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.print_test("Get transactions", False, str(e))
            return False
            
    def test_agent_analysis(self):
        """Test multi-agent analysis endpoint"""
        self.print_header("TESTING MULTI-AGENT ANALYSIS")
        
        try:
            payload = {
                "user_id": self.user_id,
                "days": 30,
                "target_savings_rate": 0.30,
                "risk_tolerance": "moderate"
            }
            
            headers = {"Authorization": f"Bearer {self.token}"}
            
            print(f"{YELLOW}Starting agent analysis (this may take 10-30 seconds)...{RESET}\n")
            start_time = time.time()
            
            response = requests.post(
                f"{API_BASE_URL}/api/finance/agent-analysis",
                json=payload,
                headers=headers,
                timeout=60
            )
            
            duration = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                
                self.print_test("Agent analysis endpoint", True, f"Completed in {duration:.2f}s")
                
                # Check executive summary
                exec_summary = data.get("executive_summary", {})
                if exec_summary:
                    self.print_test("Executive summary", True, 
                                  f"Health Score: {exec_summary.get('health_score')}/100")
                    self.print_test("Risk assessment", True, 
                                  f"Risk Level: {exec_summary.get('risk_level')}")
                    self.print_test("Overall status", True, 
                                  f"Status: {exec_summary.get('overall_status')}")
                
                # Check financial overview
                fin_overview = data.get("financial_overview", {})
                if fin_overview:
                    self.print_test("Financial overview", True, 
                                  f"Income: ₹{fin_overview.get('total_income', 0):,.2f}")
                    self.print_test("Savings rate", True, 
                                  f"{fin_overview.get('savings_rate', 0)*100:.1f}%")
                
                # Check budget plan
                budget_plan = data.get("budget_plan", {})
                if budget_plan:
                    allocations = budget_plan.get("allocations", {})
                    self.print_test("Budget optimization", bool(allocations), 
                                  f"{len(allocations)} categories")
                
                # Check risk assessment
                risk_data = data.get("risk_assessment", {})
                if risk_data:
                    risks = risk_data.get("risks", {})
                    self.print_test("Risk analysis", bool(risks), 
                                  f"{len(risks)} risk categories evaluated")
                
                # Check savings strategy
                savings = data.get("savings_strategy", {})
                if savings:
                    self.print_test("Savings strategy", bool(savings), 
                                  f"Target: ₹{savings.get('target_monthly_savings', 0):,.2f}/month")
                
                # Check monitoring alerts
                monitoring = data.get("monitoring_alerts", {})
                if monitoring:
                    alerts = monitoring.get("alerts", [])
                    self.print_test("Monitoring alerts", True, 
                                  f"{len(alerts)} alerts generated")
                
                return True
            else:
                self.print_test("Agent analysis endpoint", False, 
                              f"Status: {response.status_code}")
                try:
                    error_detail = response.json()
                    print(f"  {RED}Error: {error_detail}{RESET}")
                except:
                    print(f"  {RED}Response: {response.text[:200]}{RESET}")
                return False
        except requests.Timeout:
            self.print_test("Agent analysis endpoint", False, "Request timeout (>60s)")
            return False
        except Exception as e:
            self.print_test("Agent analysis endpoint", False, str(e))
            return False
            
    def test_forecast_generation(self):
        """Test forecast generation"""
        self.print_header("TESTING FORECAST GENERATION")
        
        try:
            payload = {
                "user_id": self.user_id,
                "forecast_days": 7,
                "include_confidence": True
            }
            
            headers = {"Authorization": f"Bearer {self.token}"}
            response = requests.post(
                f"{API_BASE_URL}/api/finance/forecast",
                json=payload,
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                income_forecast = data.get("income_forecast", [])
                expense_forecast = data.get("expense_forecast", [])
                
                self.print_test("Income forecast", bool(income_forecast), 
                              f"{len(income_forecast)} days predicted")
                self.print_test("Expense forecast", bool(expense_forecast), 
                              f"{len(expense_forecast)} days predicted")
                
                if income_forecast:
                    has_confidence = all("lower" in f and "upper" in f for f in income_forecast)
                    self.print_test("Confidence intervals", has_confidence, 
                                  "Prophet confidence bands included")
                
                return True
            else:
                self.print_test("Forecast generation", False, 
                              f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.print_test("Forecast generation", False, str(e))
            return False
            
    def test_budget_optimization(self):
        """Test budget optimization"""
        self.print_header("TESTING BUDGET OPTIMIZATION")
        
        try:
            payload = {
                "user_id": self.user_id,
                "target_savings_rate": 0.25,
                "risk_tolerance": "moderate"
            }
            
            headers = {"Authorization": f"Bearer {self.token}"}
            response = requests.post(
                f"{API_BASE_URL}/api/finance/budget/optimize",
                json=payload,
                headers=headers,
                timeout=20
            )
            
            if response.status_code == 200:
                data = response.json()
                allocations = data.get("optimized_budget", {})
                
                self.print_test("Budget optimization", bool(allocations), 
                              f"{len(allocations)} categories optimized")
                
                if allocations:
                    total = sum(allocations.values())
                    self.print_test("Budget total", total > 0, f"₹{total:,.2f}")
                
                return True
            else:
                self.print_test("Budget optimization", False, 
                              f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.print_test("Budget optimization", False, str(e))
            return False
            
    def test_insights_generation(self):
        """Test AI insights generation"""
        self.print_header("TESTING AI INSIGHTS")
        
        try:
            payload = {
                "user_id": self.user_id,
                "context": None
            }
            
            headers = {"Authorization": f"Bearer {self.token}"}
            response = requests.post(
                f"{API_BASE_URL}/api/finance/insights",
                json=payload,
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                insights = data.get("insights", [])
                
                self.print_test("AI insights", bool(insights), 
                              f"{len(insights)} insights generated")
                
                if insights:
                    priorities = set(i.get("priority") for i in insights)
                    self.print_test("Insight priorities", bool(priorities), 
                                  f"Priorities: {', '.join(priorities)}")
                
                return True
            else:
                self.print_test("AI insights", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.print_test("AI insights", False, str(e))
            return False
            
    def test_anomaly_detection(self):
        """Test anomaly detection"""
        self.print_header("TESTING ANOMALY DETECTION")
        
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            response = requests.get(
                f"{API_BASE_URL}/api/finance/anomalies",
                params={"user_id": self.user_id},
                headers=headers,
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                anomalies = data.get("anomalies", [])
                
                self.print_test("Anomaly detection", True, 
                              f"{len(anomalies)} anomalies detected")
                
                if anomalies:
                    types = set(a.get("type") for a in anomalies)
                    self.print_test("Anomaly types", bool(types), 
                                  f"Types: {', '.join(types)}")
                
                return True
            else:
                self.print_test("Anomaly detection", False, 
                              f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.print_test("Anomaly detection", False, str(e))
            return False
            
    def print_summary(self):
        """Print final test summary"""
        self.print_header("TEST SUMMARY")
        
        total = self.test_results["total"]
        passed = self.test_results["passed"]
        failed = self.test_results["failed"]
        success_rate = (passed / total * 100) if total > 0 else 0
        
        print(f"{BOLD}Total Tests:{RESET} {total}")
        print(f"{GREEN}{BOLD}Passed:{RESET} {passed}")
        print(f"{RED}{BOLD}Failed:{RESET} {failed}")
        print(f"{BOLD}Success Rate:{RESET} {success_rate:.1f}%\n")
        
        if success_rate == 100:
            print(f"{GREEN}{BOLD}🎉 ALL TESTS PASSED!{RESET}")
            print(f"{GREEN}FinSage AI is fully operational.{RESET}\n")
        elif success_rate >= 80:
            print(f"{YELLOW}{BOLD}⚠️  MOST TESTS PASSED{RESET}")
            print(f"{YELLOW}System is mostly operational with some issues.{RESET}\n")
        else:
            print(f"{RED}{BOLD}❌ MULTIPLE TESTS FAILED{RESET}")
            print(f"{RED}System needs attention before production use.{RESET}\n")
            
    def run_all_tests(self):
        """Run complete test suite"""
        print(f"\n{BOLD}{'='*70}{RESET}")
        print(f"{BOLD}{BLUE}FinSage AI - Comprehensive Test Suite{RESET}")
        print(f"{BOLD}{'='*70}{RESET}")
        print(f"Target: {API_BASE_URL}")
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        # Core API tests
        if not self.test_health_check():
            print(f"\n{RED}Backend is not responding. Make sure it's running on {API_BASE_URL}{RESET}")
            return False
            
        # Authentication tests
        self.test_register()
        self.test_login()
        self.test_profile_update()
        
        # Transaction tests
        self.test_create_transactions()
        self.test_get_transactions()
        
        # AI/ML Feature tests
        self.test_agent_analysis()
        self.test_forecast_generation()
        self.test_budget_optimization()
        self.test_insights_generation()
        self.test_anomaly_detection()
        
        # Print summary
        self.print_summary()
        
        return self.test_results["failed"] == 0

def main():
    tester = APITester()
    success = tester.run_all_tests()
    return 0 if success else 1

if __name__ == "__main__":
    import sys
    sys.exit(main())
