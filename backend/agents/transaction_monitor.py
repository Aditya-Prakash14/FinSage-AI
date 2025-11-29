"""
Transaction Monitor Agent
Monitors transactions in real-time and provides alerts
"""

from typing import Dict, Any, List
from .base_agent import BaseAgent


class TransactionMonitorAgent(BaseAgent):
    """
    Expert in real-time transaction monitoring and anomaly detection
    
    Responsibilities:
    - Monitor transactions for anomalies
    - Detect unusual spending patterns
    - Identify budget overruns
    - Provide real-time alerts
    """
    
    def __init__(self):
        super().__init__(
            agent_name="Transaction Monitor",
            role="Monitors transactions and detects anomalies",
            temperature=0.1  # Very low for factual monitoring
        )
    
    def get_system_prompt(self) -> str:
        return """You are a Transaction Monitoring specialist for Indian gig workers.

Your expertise:
- Detecting unusual spending patterns
- Identifying duplicate or suspicious transactions
- Flagging budget category overruns
- Recognizing spending anomalies

Guidelines:
- Be objective and data-driven
- Distinguish between unusual and concerning
- Consider context (festivals, emergencies)
- Provide clear, actionable alerts
- Don't raise false alarms unnecessarily

Format alerts with severity: Info/Warning/Urgent."""
    
    def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Monitor transactions and generate alerts
        
        Args:
            state: Must contain 'transactions', 'budget_recommendation'
        
        Returns:
            Updated state with 'monitoring_alerts'
        """
        self.log("Monitoring transactions...")
        
        transactions = state.get("transactions", [])
        budget = state.get("budget_recommendation", {})
        analysis = state.get("financial_analysis", {})
        
        if not transactions:
            state["monitoring_alerts"] = {
                "alerts": [],
                "summary": "No transactions to monitor"
            }
            return state
        
        # Detect anomalies
        anomalies = self._detect_anomalies(transactions)
        
        # Check budget overruns
        budget_alerts = self._check_budget_overruns(transactions, budget)
        
        # Check for duplicate transactions
        duplicate_alerts = self._check_duplicates(transactions)
        
        # Combine all alerts
        all_alerts = anomalies + budget_alerts + duplicate_alerts
        
        # Get AI interpretation for significant alerts
        if all_alerts:
            alert_prompt = self._create_alert_prompt(all_alerts, transactions)
            response = self.invoke_llm(alert_prompt)
            ai_interpretation = self.extract_json(response)
            
            if not ai_interpretation:
                ai_interpretation = {"summary": "Monitoring alerts detected", "action_needed": True}
        else:
            ai_interpretation = {"summary": "All transactions normal", "action_needed": False}
        
        # Sort alerts by severity
        all_alerts.sort(key=lambda x: self._severity_order(x.get("severity", "info")))
        
        state["monitoring_alerts"] = {
            "alerts": all_alerts,
            "alert_count": len(all_alerts),
            "ai_interpretation": ai_interpretation,
            "requires_action": len([a for a in all_alerts if a.get("severity") in ["urgent", "warning"]]) > 0
        }
        
        self.log(f"Monitoring complete: {len(all_alerts)} alerts generated")
        
        return state
    
    def _detect_anomalies(self, transactions: List[Dict]) -> List[Dict]:
        """Detect unusual transaction amounts using statistical methods"""
        import numpy as np
        
        alerts = []
        
        # Filter expense transactions
        expenses = [abs(t.get("amount", 0)) for t in transactions if t.get("type") == "debit"]
        
        if len(expenses) < 5:
            return alerts  # Not enough data
        
        # Calculate statistical thresholds
        mean_expense = np.mean(expenses)
        std_expense = np.std(expenses)
        threshold_high = mean_expense + (2.5 * std_expense)  # 2.5 standard deviations
        threshold_very_high = mean_expense + (3 * std_expense)
        
        # Check each transaction
        for txn in transactions:
            if txn.get("type") != "debit":
                continue
            
            amount = abs(txn.get("amount", 0))
            
            if amount > threshold_very_high:
                alerts.append({
                    "type": "anomaly",
                    "severity": "urgent",
                    "transaction": txn,
                    "message": f"Unusually high expense: ₹{amount:.2f} (expected ~₹{mean_expense:.2f})",
                    "deviation": ((amount - mean_expense) / mean_expense) * 100
                })
            elif amount > threshold_high:
                alerts.append({
                    "type": "anomaly",
                    "severity": "warning",
                    "transaction": txn,
                    "message": f"Higher than usual expense: ₹{amount:.2f}",
                    "deviation": ((amount - mean_expense) / mean_expense) * 100
                })
        
        return alerts
    
    def _check_budget_overruns(self, transactions: List[Dict], budget: Dict) -> List[Dict]:
        """Check if spending exceeds budget allocations"""
        alerts = []
        
        budget_allocation = budget.get("budget_allocation", {})
        if not budget_allocation:
            return alerts
        
        # Calculate spending by category
        from collections import defaultdict
        category_spending = defaultdict(float)
        
        for txn in transactions:
            if txn.get("type") == "debit":
                cat = txn.get("category", "miscellaneous")
                category_spending[cat] += abs(txn.get("amount", 0))
        
        # Check each category against budget
        for category, spent in category_spending.items():
            budgeted = budget_allocation.get(category, 0)
            
            if budgeted == 0:
                continue
            
            overspend_pct = ((spent - budgeted) / budgeted) * 100
            
            if overspend_pct > 20:
                alerts.append({
                    "type": "budget_overrun",
                    "severity": "urgent",
                    "category": category,
                    "message": f"{category}: Over budget by {overspend_pct:.1f}% (₹{spent:.2f}/₹{budgeted:.2f})",
                    "spent": spent,
                    "budgeted": budgeted,
                    "overspend_pct": overspend_pct
                })
            elif overspend_pct > 10:
                alerts.append({
                    "type": "budget_overrun",
                    "severity": "warning",
                    "category": category,
                    "message": f"{category}: Approaching budget limit ({overspend_pct:.1f}% over)",
                    "spent": spent,
                    "budgeted": budgeted,
                    "overspend_pct": overspend_pct
                })
        
        return alerts
    
    def _check_duplicates(self, transactions: List[Dict]) -> List[Dict]:
        """Check for potential duplicate transactions"""
        alerts = []
        
        # Group transactions by amount and date
        from collections import defaultdict
        from datetime import datetime, timedelta
        
        # Create a simple hash for each transaction
        txn_groups = defaultdict(list)
        
        for i, txn in enumerate(transactions):
            # Create key: amount + date (day) + category
            try:
                txn_date = txn.get("date")
                if isinstance(txn_date, str):
                    txn_date = datetime.fromisoformat(txn_date.replace('Z', '+00:00'))
                
                date_key = txn_date.date() if isinstance(txn_date, datetime) else str(txn_date)
                amount = round(txn.get("amount", 0), 2)
                category = txn.get("category", "")
                
                key = f"{amount}_{date_key}_{category}"
                txn_groups[key].append((i, txn))
            except:
                continue
        
        # Find groups with multiple transactions
        for key, group in txn_groups.items():
            if len(group) > 1:
                txn_list = [t[1] for t in group]
                alerts.append({
                    "type": "duplicate",
                    "severity": "info",
                    "message": f"Possible duplicate: {len(group)} transactions of ₹{txn_list[0].get('amount', 0):.2f} on same day",
                    "transactions": txn_list,
                    "count": len(group)
                })
        
        return alerts
    
    def _create_alert_prompt(self, alerts: List[Dict], transactions: List[Dict]) -> str:
        """Create prompt for AI interpretation of alerts"""
        alert_summary = []
        
        for alert in alerts[:5]:  # Top 5 alerts
            alert_summary.append(
                f"- [{alert.get('severity', 'info').upper()}] {alert.get('message', '')}"
            )
        
        return f"""Interpret these transaction monitoring alerts:

ALERTS ({len(alerts)} total):
{chr(10).join(alert_summary)}

TRANSACTION COUNT: {len(transactions)}

Provide:
1. Brief summary of what's happening (1-2 sentences)
2. Is immediate action needed? (yes/no)
3. Top priority action to take

Format as JSON with keys: summary, action_needed (boolean), priority_action"""
    
    def _severity_order(self, severity: str) -> int:
        """Return numeric order for severity sorting"""
        order = {"urgent": 0, "warning": 1, "info": 2}
        return order.get(severity.lower(), 3)
