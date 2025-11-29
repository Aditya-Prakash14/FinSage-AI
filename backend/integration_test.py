"""
Comprehensive integration test for FinSage AI
Tests both database and agent system
"""

import sys
import os
from datetime import datetime, timedelta
import random

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def generate_sample_transactions(days=30):
    """Generate sample transaction data"""
    transactions = []
    base_date = datetime.now() - timedelta(days=days)
    
    categories = {
        "credit": ["salary", "freelance", "gig_income"],
        "debit": ["food_groceries", "rent_utilities", "transportation", "entertainment", "healthcare"]
    }
    
    for day in range(days):
        current_date = base_date + timedelta(days=day)
        
        # Random income (every 7-10 days)
        if day % random.randint(7, 10) == 0:
            transactions.append({
                "date": current_date.isoformat(),
                "amount": random.uniform(15000, 35000),
                "type": "credit",
                "category": random.choice(categories["credit"]),
                "description": "Income received",
                "source": "bank_transfer"
            })
        
        # Daily expenses
        for _ in range(random.randint(1, 4)):
            transactions.append({
                "date": current_date.isoformat(),
                "amount": -random.uniform(50, 2000),
                "type": "debit",
                "category": random.choice(categories["debit"]),
                "description": "Expense",
                "source": "upi"
            })
    
    return transactions


def test_database():
    """Test database connection"""
    print("=" * 70)
    print("🔌 Testing Database Connection")
    print("=" * 70)
    print()
    
    try:
        from database.mongo_config import mongodb_manager
        
        print("Attempting to connect to MongoDB...")
        mongodb_manager.connect()
        
        db = mongodb_manager.get_database()
        if db is not None:
            print("✅ Database connected successfully!")
            
            # Try to get stats
            try:
                stats = db.command("dbStats")
                print(f"   Database: {stats.get('db', 'N/A')}")
                print(f"   Collections: {stats.get('collections', 0)}")
                print(f"   Data Size: {stats.get('dataSize', 0) / 1024:.2f} KB")
                return True
            except Exception as e:
                print(f"⚠️  Database connected but couldn't get stats: {e}")
                return True
        else:
            print("⚠️  Database not available - will use demo mode")
            return False
    
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False


def test_agents():
    """Test agent system"""
    print()
    print("=" * 70)
    print("🤖 Testing Multi-Agent System")
    print("=" * 70)
    print()
    
    try:
        from agents.orchestrator import get_orchestrator
        
        print("Generating sample transactions...")
        transactions = generate_sample_transactions(30)
        print(f"   Created {len(transactions)} transactions")
        print()
        
        user_preferences = {
            "target_savings_rate": 0.20,
            "risk_tolerance": "medium"
        }
        
        print("Running multi-agent analysis...")
        orchestrator = get_orchestrator()
        report = orchestrator.analyze(
            user_id="integration_test_user",
            transactions=transactions,
            user_preferences=user_preferences
        )
        
        print()
        print("📊 ANALYSIS RESULTS:")
        print("-" * 70)
        
        summary = report.get("executive_summary", {})
        print(f"Overall Status: {summary.get('overall_status', 'N/A')}")
        print(f"Health Score: {summary.get('health_score', 0):.1f}/100")
        print(f"Risk Level: {summary.get('risk_level', 'N/A')}")
        
        metrics = summary.get("key_metrics", {})
        print(f"\nIncome: ₹{metrics.get('monthly_income', 0):,.2f}")
        print(f"Expenses: ₹{metrics.get('monthly_expenses', 0):,.2f}")
        print(f"Savings Rate: {metrics.get('savings_rate', 0):.1f}%")
        
        print(f"\n✅ Agent system working correctly!")
        print(f"   Analysis Duration: {report.get('workflow_duration', 0):.2f}s")
        
        return True
        
    except Exception as e:
        print(f"❌ Agent test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_backend_api():
    """Test if backend API endpoint works"""
    print()
    print("=" * 70)
    print("🌐 Testing Backend API Integration")
    print("=" * 70)
    print()
    
    try:
        import requests
        
        print("Checking if backend is running...")
        try:
            response = requests.get("http://localhost:8000/api/finance/health", timeout=2)
            if response.status_code == 200:
                print("✅ Backend API is running!")
                print(f"   Response: {response.json()}")
                return True
            else:
                print(f"⚠️  Backend returned status {response.status_code}")
                return False
        except requests.exceptions.ConnectionError:
            print("⚠️  Backend is not running on port 8000")
            print("   Start backend with: cd backend && python main.py")
            return False
        except Exception as e:
            print(f"❌ API test failed: {e}")
            return False
            
    except ImportError:
        print("⚠️  requests library not installed - skipping API test")
        return None


def main():
    """Run all integration tests"""
    print("\n")
    print("╔══════════════════════════════════════════════════════════════════╗")
    print("║          FINSAGE AI INTEGRATION TEST SUITE                       ║")
    print("╚══════════════════════════════════════════════════════════════════╝")
    print()
    
    results = {}
    
    # Test 1: Database
    results['database'] = test_database()
    
    # Test 2: Agents
    results['agents'] = test_agents()
    
    # Test 3: Backend API
    results['api'] = test_backend_api()
    
    # Summary
    print()
    print("=" * 70)
    print("📋 TEST SUMMARY")
    print("=" * 70)
    print()
    
    tests_passed = 0
    tests_total = 0
    
    for test_name, result in results.items():
        if result is not None:
            tests_total += 1
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{test_name.upper():20s}: {status}")
            if result:
                tests_passed += 1
        else:
            print(f"{test_name.upper():20s}: ⏭️  SKIPPED")
    
    print()
    print(f"Tests Passed: {tests_passed}/{tests_total}")
    
    if tests_passed == tests_total:
        print()
        print("🎉 ALL TESTS PASSED!")
        print()
        print("System Status:")
        print(f"  {'Database:':15s} {'✅ Connected' if results.get('database') else '⚠️  Offline (demo mode)'}")
        print(f"  {'Agents:':15s} {'✅ Operational' if results.get('agents') else '❌ Failed'}")
        print(f"  {'Backend API:':15s} {'✅ Running' if results.get('api') else '⚠️  Not started'}")
        print()
        
        if not results.get('database'):
            print("💡 Note: Database is offline. The system will work in demo mode.")
            print("   To fix: Check your MongoDB Atlas connection and SSL settings.")
        
        if not results.get('api'):
            print("💡 Note: Backend API is not running.")
            print("   To start: cd backend && python main.py")
        
    else:
        print()
        print("⚠️  SOME TESTS FAILED")
        print("   Review the errors above for details.")
    
    print()
    print("=" * 70)
    
    return tests_passed == tests_total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
