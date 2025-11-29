"""
Risk Assessor Agent
Evaluates financial risks and provides warnings
"""

from typing import Dict, Any
from .base_agent import BaseAgent


class RiskAssessorAgent(BaseAgent):
    """
    Expert in identifying and assessing financial risks
    
    Responsibilities:
    - Assess income stability risk
    - Identify overspending patterns
    - Evaluate emergency fund adequacy
    - Warn about potential cash flow problems
    """
    
    def __init__(self):
        super().__init__(
            agent_name="Risk Assessor",
            role="Identifies and evaluates financial risks",
            temperature=0.2
        )
    
    def get_system_prompt(self) -> str:
        return """You are a Financial Risk Assessment specialist for gig workers in India.

Your expertise:
- Evaluating income stability and volatility risks
- Identifying cash flow vulnerabilities
- Assessing emergency fund adequacy
- Detecting overspending patterns
- Predicting potential financial crises

Guidelines:
- Be clear but not alarmist
- Prioritize risks by severity
- Provide actionable mitigation strategies
- Consider the unique challenges of gig work
- Use Indian economic context

Format risk assessments with severity levels (Low/Medium/High/Critical)."""
    
    def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Assess financial risks
        
        Args:
            state: Must contain 'financial_analysis', 'budget_recommendation'
        
        Returns:
            Updated state with 'risk_assessment'
        """
        self.log("Assessing financial risks...")
        
        analysis = state.get("financial_analysis", {})
        metrics = analysis.get("metrics", {})
        budget = state.get("budget_recommendation", {})
        
        if not metrics:
            state["risk_assessment"] = {
                "error": "No data for risk assessment"
            }
            return state
        
        # Calculate risk scores
        risks = self._calculate_risk_scores(metrics, budget)
        
        # Generate AI risk analysis
        risk_prompt = f"""Assess financial risks for this gig worker:

FINANCIAL METRICS:
- Income Volatility: {metrics.get('income_volatility', 0):.2f}
- Savings Rate: {metrics.get('savings_rate', 0):.1f}%
- Cash Flow: ₹{metrics.get('net_cash_flow', 0):.2f}
- Expense Ratio: {(metrics.get('total_expenses', 0) / metrics.get('total_income', 1)) * 100:.1f}%

CALCULATED RISKS:
- Income Stability Risk: {risks['income_stability_risk']['score']:.2f} ({risks['income_stability_risk']['level']})
- Cash Flow Risk: {risks['cash_flow_risk']['score']:.2f} ({risks['cash_flow_risk']['level']})
- Savings Risk: {risks['savings_risk']['score']:.2f} ({risks['savings_risk']['level']})
- Emergency Fund Risk: {risks['emergency_fund_risk']['score']:.2f} ({risks['emergency_fund_risk']['level']})

Provide:
1. Overall risk level (Low/Medium/High/Critical)
2. Top 3 priority risks to address
3. Specific mitigation actions for each priority risk
4. Timeline for action (immediate/1-month/3-months)

Format as JSON with keys: overall_risk_level, priority_risks (array of objects with 'risk', 'severity', 'mitigation', 'timeline')"""
        
        response = self.invoke_llm(risk_prompt)
        ai_assessment = self.extract_json(response)
        
        if not ai_assessment:
            ai_assessment = self._fallback_assessment(risks)
        
        state["risk_assessment"] = {
            "risk_scores": risks,
            "ai_assessment": ai_assessment,
            "overall_risk_score": self._calculate_overall_risk(risks),
            "timestamp": self._get_timestamp()
        }
        
        overall_level = ai_assessment.get("overall_risk_level", "Medium")
        self.log(f"Risk assessment complete: Overall risk level = {overall_level}")
        
        return state
    
    def _calculate_risk_scores(self, metrics: Dict, budget: Dict) -> Dict[str, Dict]:
        """
        Calculate individual risk scores
        
        Returns dict of risks with score (0-1) and level (Low/Medium/High/Critical)
        """
        risks = {}
        
        # 1. Income Stability Risk (based on volatility)
        income_volatility = metrics.get("income_volatility", 0)
        if income_volatility < 0.2:
            income_risk_score = 0.1
            income_risk_level = "Low"
        elif income_volatility < 0.4:
            income_risk_score = 0.3
            income_risk_level = "Medium"
        elif income_volatility < 0.6:
            income_risk_score = 0.6
            income_risk_level = "High"
        else:
            income_risk_score = 0.9
            income_risk_level = "Critical"
        
        risks["income_stability_risk"] = {
            "score": income_risk_score,
            "level": income_risk_level,
            "description": f"Income volatility of {income_volatility:.2f}"
        }
        
        # 2. Cash Flow Risk
        net_cash_flow = metrics.get("net_cash_flow", 0)
        total_income = metrics.get("total_income", 1)
        
        if net_cash_flow > 0 and net_cash_flow > total_income * 0.2:
            cash_flow_risk_score = 0.1
            cash_flow_risk_level = "Low"
        elif net_cash_flow > 0:
            cash_flow_risk_score = 0.3
            cash_flow_risk_level = "Medium"
        elif net_cash_flow > -total_income * 0.1:
            cash_flow_risk_score = 0.6
            cash_flow_risk_level = "High"
        else:
            cash_flow_risk_score = 0.9
            cash_flow_risk_level = "Critical"
        
        risks["cash_flow_risk"] = {
            "score": cash_flow_risk_score,
            "level": cash_flow_risk_level,
            "description": f"Net cash flow: ₹{net_cash_flow:.2f}"
        }
        
        # 3. Savings Risk
        savings_rate = metrics.get("savings_rate", 0)
        if savings_rate >= 20:
            savings_risk_score = 0.1
            savings_risk_level = "Low"
        elif savings_rate >= 10:
            savings_risk_score = 0.3
            savings_risk_level = "Medium"
        elif savings_rate >= 0:
            savings_risk_score = 0.6
            savings_risk_level = "High"
        else:
            savings_risk_score = 0.9
            savings_risk_level = "Critical"
        
        risks["savings_risk"] = {
            "score": savings_risk_score,
            "level": savings_risk_level,
            "description": f"Savings rate: {savings_rate:.1f}%"
        }
        
        # 4. Emergency Fund Risk (assume 0 for new users)
        # In production, this would check actual emergency fund balance
        emergency_months = 0  # This should come from user data
        
        if emergency_months >= 6:
            ef_risk_score = 0.1
            ef_risk_level = "Low"
        elif emergency_months >= 3:
            ef_risk_score = 0.3
            ef_risk_level = "Medium"
        elif emergency_months >= 1:
            ef_risk_score = 0.6
            ef_risk_level = "High"
        else:
            ef_risk_score = 0.9
            ef_risk_level = "Critical"
        
        risks["emergency_fund_risk"] = {
            "score": ef_risk_score,
            "level": ef_risk_level,
            "description": f"Emergency fund: {emergency_months} months coverage"
        }
        
        return risks
    
    def _calculate_overall_risk(self, risks: Dict[str, Dict]) -> float:
        """Calculate weighted overall risk score"""
        weights = {
            "income_stability_risk": 0.3,
            "cash_flow_risk": 0.3,
            "savings_risk": 0.2,
            "emergency_fund_risk": 0.2
        }
        
        overall = sum(
            risks[risk]["score"] * weight 
            for risk, weight in weights.items()
            if risk in risks
        )
        
        return overall
    
    def _fallback_assessment(self, risks: Dict) -> Dict:
        """Generate fallback risk assessment"""
        # Find top 3 risks by score
        sorted_risks = sorted(
            [(name, data) for name, data in risks.items()],
            key=lambda x: -x[1]["score"]
        )
        
        priority_risks = []
        for name, data in sorted_risks[:3]:
            risk_name = name.replace("_", " ").title()
            
            # Determine mitigation
            if "income" in name.lower():
                mitigation = "Diversify income sources, build larger emergency fund"
                timeline = "3-months"
            elif "cash_flow" in name.lower():
                mitigation = "Reduce discretionary spending immediately, increase income"
                timeline = "immediate"
            elif "savings" in name.lower():
                mitigation = "Cut 10% from discretionary categories, automate savings"
                timeline = "1-month"
            else:
                mitigation = "Build emergency fund with 10% of each income"
                timeline = "3-months"
            
            priority_risks.append({
                "risk": risk_name,
                "severity": data["level"],
                "mitigation": mitigation,
                "timeline": timeline
            })
        
        # Determine overall risk
        overall_score = self._calculate_overall_risk(risks)
        if overall_score < 0.3:
            overall_level = "Low"
        elif overall_score < 0.5:
            overall_level = "Medium"
        elif overall_score < 0.7:
            overall_level = "High"
        else:
            overall_level = "Critical"
        
        return {
            "overall_risk_level": overall_level,
            "priority_risks": priority_risks
        }
    
    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.utcnow().isoformat()
