"""
Financial Analyst Agent
Analyzes transaction data, identifies patterns, and provides insights
"""

from typing import Dict, Any
from datetime import datetime, timedelta
from .base_agent import BaseAgent


class FinancialAnalystAgent(BaseAgent):
    """
    Expert in analyzing financial data and identifying trends
    
    Responsibilities:
    - Analyze transaction patterns
    - Calculate key financial metrics
    - Identify spending trends
    - Detect anomalies
    """
    
    def __init__(self):
        super().__init__(
            agent_name="Financial Analyst",
            role="Analyzes financial data and identifies patterns",
            temperature=0.2  # Lower temperature for more factual analysis
        )
    
    def get_system_prompt(self) -> str:
        return """You are a Financial Analyst specializing in personal finance for gig workers in India.

Your expertise:
- Analyzing income and expense patterns
- Identifying financial trends and anomalies
- Calculating key financial health metrics
- Understanding cash flow volatility

Guidelines:
- Be data-driven and objective
- Highlight both positive and concerning patterns
- Consider the irregular income nature of gig work
- Use Indian context (₹, UPI, informal income)
- Provide specific numerical insights

Format your analysis clearly with bullet points and metrics."""
    
    def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze financial data and update state
        
        Args:
            state: Must contain 'transactions', 'user_id'
        
        Returns:
            Updated state with 'financial_analysis'
        """
        self.log("Starting financial analysis...")
        
        transactions = state.get("transactions", [])
        if not transactions:
            state["financial_analysis"] = {
                "error": "No transaction data available",
                "metrics": {}
            }
            return state
        
        # Calculate metrics
        metrics = self._calculate_metrics(transactions)
        
        # Identify patterns
        patterns = self._identify_patterns(transactions)
        
        # Generate AI insights
        analysis_prompt = f"""Analyze this financial data for a gig worker:

METRICS:
- Total Income (30 days): ₹{metrics['total_income']:.2f}
- Total Expenses (30 days): ₹{metrics['total_expenses']:.2f}
- Net Cash Flow: ₹{metrics['net_cash_flow']:.2f}
- Savings Rate: {metrics['savings_rate']:.1f}%
- Income Volatility: {metrics['income_volatility']:.2f}
- Average Transaction: ₹{metrics['avg_transaction']:.2f}
- Transaction Count: {metrics['transaction_count']}

PATTERNS:
{patterns}

Provide:
1. Overall financial health assessment (1-2 sentences)
2. Top 3 key findings
3. Main concerns or risks
4. Positive aspects to reinforce

Format as JSON with keys: health_assessment, key_findings (array), concerns (array), positives (array)"""
        
        response = self.invoke_llm(analysis_prompt)
        analysis_data = self.extract_json(response)
        
        if not analysis_data:
            # Fallback analysis
            analysis_data = self._fallback_analysis(metrics, patterns)
        
        state["financial_analysis"] = {
            "metrics": metrics,
            "patterns": patterns,
            "insights": analysis_data,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        self.log(f"Analysis complete: {metrics['transaction_count']} transactions analyzed")
        
        return state
    
    def _calculate_metrics(self, transactions: list) -> Dict[str, float]:
        """Calculate key financial metrics"""
        import numpy as np
        
        income_txns = [t for t in transactions if t.get("type") == "credit"]
        expense_txns = [t for t in transactions if t.get("type") == "debit"]
        
        total_income = sum(t.get("amount", 0) for t in income_txns)
        total_expenses = sum(abs(t.get("amount", 0)) for t in expense_txns)
        net_cash_flow = total_income - total_expenses
        
        savings_rate = (net_cash_flow / total_income * 100) if total_income > 0 else 0
        
        # Calculate income volatility (coefficient of variation)
        income_amounts = [t.get("amount", 0) for t in income_txns]
        if len(income_amounts) > 1:
            income_volatility = np.std(income_amounts) / np.mean(income_amounts) if np.mean(income_amounts) > 0 else 0
        else:
            income_volatility = 0
        
        avg_transaction = (total_income + total_expenses) / len(transactions) if transactions else 0
        
        return {
            "total_income": total_income,
            "total_expenses": total_expenses,
            "net_cash_flow": net_cash_flow,
            "savings_rate": savings_rate,
            "income_volatility": income_volatility,
            "avg_transaction": avg_transaction,
            "transaction_count": len(transactions),
            "income_count": len(income_txns),
            "expense_count": len(expense_txns)
        }
    
    def _identify_patterns(self, transactions: list) -> str:
        """Identify spending and income patterns"""
        from collections import defaultdict
        
        # Category breakdown
        category_spending = defaultdict(float)
        for txn in transactions:
            if txn.get("type") == "debit":
                cat = txn.get("category", "Uncategorized")
                category_spending[cat] += abs(txn.get("amount", 0))
        
        # Sort categories by spending
        sorted_cats = sorted(category_spending.items(), key=lambda x: -x[1])
        
        pattern_text = "Top Spending Categories:\n"
        for cat, amount in sorted_cats[:5]:
            pattern_text += f"- {cat}: ₹{amount:.2f}\n"
        
        # Day of week patterns (if date available)
        try:
            import pandas as pd
            df = pd.DataFrame([
                {
                    "date": t.get("date"),
                    "amount": abs(t.get("amount", 0)),
                    "type": t.get("type")
                }
                for t in transactions if t.get("date")
            ])
            
            if not df.empty:
                df["date"] = pd.to_datetime(df["date"])
                df["day_of_week"] = df["date"].dt.day_name()
                
                day_spending = df[df["type"] == "debit"].groupby("day_of_week")["amount"].sum()
                if not day_spending.empty:
                    peak_day = day_spending.idxmax()
                    pattern_text += f"\nPeak spending day: {peak_day} (₹{day_spending[peak_day]:.2f})"
        except:
            pass
        
        return pattern_text
    
    def _fallback_analysis(self, metrics: Dict, patterns: str) -> Dict:
        """Generate fallback analysis when LLM unavailable"""
        health_assessment = "Financial analysis complete. "
        
        if metrics['net_cash_flow'] > 0:
            health_assessment += f"Positive cash flow of ₹{metrics['net_cash_flow']:.2f}."
        else:
            health_assessment += f"Negative cash flow of ₹{metrics['net_cash_flow']:.2f} - expenses exceed income."
        
        key_findings = [
            f"Savings rate: {metrics['savings_rate']:.1f}%",
            f"Income volatility: {metrics['income_volatility']:.2f}",
            f"{metrics['transaction_count']} transactions processed"
        ]
        
        concerns = []
        if metrics['net_cash_flow'] < 0:
            concerns.append("Spending exceeds income")
        if metrics['income_volatility'] > 0.5:
            concerns.append("High income volatility - build emergency fund")
        if metrics['savings_rate'] < 10:
            concerns.append("Low savings rate - aim for 15-20%")
        
        positives = []
        if metrics['net_cash_flow'] > 0:
            positives.append("Maintaining positive cash flow")
        if metrics['savings_rate'] >= 15:
            positives.append("Strong savings rate")
        if metrics['transaction_count'] > 20:
            positives.append("Good transaction tracking habits")
        
        return {
            "health_assessment": health_assessment,
            "key_findings": key_findings,
            "concerns": concerns or ["Continue monitoring financial health"],
            "positives": positives or ["Keep tracking your finances"]
        }
