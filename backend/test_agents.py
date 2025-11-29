"""
Test script for FinSage AI Multi-Agent System
"""

import sys
import os
from datetime import datetime, timedelta
import random

# Add backend to path
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
                "description": "Income received"
            })
        
        # Daily expenses
        for _ in range(random.randint(1, 4)):
            transactions.append({
                "date": current_date.isoformat(),
                "amount": -random.uniform(50, 2000),
                "type": "debit",
                "category": random.choice(categories["debit"]),
                "description": "Expense"
            })
    
    return transactions


def test_agents():
    """Test the multi-agent system"""
    print("=" * 70)
    print("🧪 Testing FinSage AI Multi-Agent System")
    print("=" * 70)
    print()
    
    try:
        from agents.orchestrator import get_orchestrator
        
        # Generate sample data
        print("📊 Generating sample transactions...")
        transactions = generate_sample_transactions(30)
        print(f"   Generated {len(transactions)} transactions")
        print()
        
        # User preferences
        user_preferences = {
            "target_savings_rate": 0.20,  # 20%
            "risk_tolerance": "medium"
        }
        
        # Run analysis
        print("🤖 Running multi-agent analysis...")
        print("   This will coordinate 5 specialized agents:")
        print("   1. Financial Analyst")
        print("   2. Budget Optimizer")
        print("   3. Risk Assessor")
        print("   4. Savings Coach")
        print("   5. Transaction Monitor")
        print()
        
        orchestrator = get_orchestrator()
        report = orchestrator.analyze(
            user_id="test_user_123",
            transactions=transactions,
            user_preferences=user_preferences
        )
        
        print()
        print("=" * 70)
        print("📋 COMPREHENSIVE FINANCIAL REPORT")
        print("=" * 70)
        print()
        
        # Executive Summary
        summary = report.get("executive_summary", {})
        print(f"Overall Status: {summary.get('overall_status', 'N/A')}")
        print(f"Financial Health Score: {summary.get('health_score', 0):.1f}/100")
        print(f"Risk Level: {summary.get('risk_level', 'N/A')}")
        print()
        
        # Key Metrics
        metrics = summary.get("key_metrics", {})
        print("💰 KEY METRICS:")
        print(f"   Monthly Income: ₹{metrics.get('monthly_income', 0):,.2f}")
        print(f"   Monthly Expenses: ₹{metrics.get('monthly_expenses', 0):,.2f}")
        print(f"   Net Cash Flow: ₹{metrics.get('net_cash_flow', 0):,.2f}")
        print(f"   Savings Rate: {metrics.get('savings_rate', 0):.1f}%")
        print()
        
        # Top Insights
        insights = summary.get("top_insights", [])
        if insights:
            print("💡 TOP INSIGHTS:")
            for i, insight in enumerate(insights, 1):
                print(f"   {i}. {insight}")
            print()
        
        # Priority Actions
        actions = summary.get("priority_actions", [])
        if actions:
            print("🎯 PRIORITY ACTIONS:")
            for i, action in enumerate(actions, 1):
                print(f"   {i}. {action}")
            print()
        
        # Alerts
        critical_alerts = summary.get("critical_alerts", [])
        if critical_alerts:
            print("⚠️  CRITICAL ALERTS:")
            for alert in critical_alerts:
                print(f"   [{alert.get('severity', 'info').upper()}] {alert.get('message', '')}")
            print()
        
        # Budget Plan
        budget = report.get("budget_plan", {})
        budget_allocation = budget.get("budget_allocation", {})
        if budget_allocation:
            print("💰 RECOMMENDED BUDGET:")
            total = sum(budget_allocation.values())
            for category, amount in sorted(budget_allocation.items(), key=lambda x: -x[1])[:5]:
                pct = (amount / total * 100) if total > 0 else 0
                print(f"   {category}: ₹{amount:,.2f} ({pct:.1f}%)")
            print(f"   Target Savings: ₹{budget.get('target_savings', 0):,.2f}")
            print()
        
        # Savings Strategy
        savings = report.get("savings_plan", {})
        strategy = savings.get("strategy", {})
        if strategy:
            print("🎯 SAVINGS STRATEGY:")
            print(f"   {strategy.get('encouragement', '')}")
            
            primary_goal = strategy.get("primary_goal", {})
            if primary_goal:
                print(f"   Primary Goal: ₹{primary_goal.get('amount', 0):,.2f}")
                print(f"   {primary_goal.get('description', '')}")
            print()
        
        # Risk Assessment
        risk = report.get("risk_profile", {})
        risk_scores = risk.get("risk_scores", {})
        if risk_scores:
            print("⚠️  RISK ASSESSMENT:")
            for risk_name, risk_data in risk_scores.items():
                risk_label = risk_name.replace("_", " ").title()
                print(f"   {risk_label}: {risk_data.get('level', 'Unknown')} (Score: {risk_data.get('score', 0):.2f})")
            print()
        
        # Workflow Info
        print("=" * 70)
        print(f"⏱️  Analysis Duration: {report.get('workflow_duration', 0):.2f} seconds")
        print(f"📅 Timestamp: {report.get('timestamp', 'N/A')}")
        
        errors = report.get("errors", [])
        if errors:
            print(f"⚠️  Errors: {len(errors)}")
            for error in errors:
                print(f"   - {error}")
        else:
            print("✅ No errors")
        
        print("=" * 70)
        print()
        print("✨ Test completed successfully!")
        print()
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_agents()
    sys.exit(0 if success else 1)
