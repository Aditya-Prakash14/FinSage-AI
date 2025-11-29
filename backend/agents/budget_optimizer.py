"""
Budget Optimizer Agent
Uses RL and AI to optimize budget allocations
"""

from typing import Dict, Any
from .base_agent import BaseAgent


class BudgetOptimizerAgent(BaseAgent):
    """
    Expert in budget planning and optimization
    
    Responsibilities:
    - Optimize budget allocations
    - Balance needs vs wants
    - Maximize savings potential
    - Adapt to income volatility
    """
    
    def __init__(self):
        super().__init__(
            agent_name="Budget Optimizer",
            role="Optimizes budget allocations for maximum savings",
            temperature=0.4
        )
    
    def get_system_prompt(self) -> str:
        return """You are a Budget Optimization specialist for Indian gig workers.

Your expertise:
- Creating realistic, achievable budgets
- Balancing essential vs discretionary spending
- Maximizing savings without compromising quality of life
- Adapting budgets to irregular income

Guidelines:
- Prioritize essentials (food, utilities, rent)
- Aim for 15-20% savings rate minimum
- Account for income volatility
- Suggest practical, specific adjustments
- Be empathetic to financial constraints
- Use Indian context (₹)

Format recommendations clearly with reasoning."""
    
    def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Optimize budget based on financial analysis
        
        Args:
            state: Must contain 'financial_analysis', 'user_preferences'
        
        Returns:
            Updated state with 'budget_recommendation'
        """
        self.log("Optimizing budget allocations...")
        
        analysis = state.get("financial_analysis", {})
        metrics = analysis.get("metrics", {})
        
        if not metrics:
            state["budget_recommendation"] = {
                "error": "No financial data for optimization"
            }
            return state
        
        # Get income and calculate available budget
        total_income = metrics.get("total_income", 0)
        current_expenses = metrics.get("total_expenses", 0)
        savings_rate = metrics.get("savings_rate", 0)
        
        # Get user preferences
        preferences = state.get("user_preferences", {})
        target_savings_rate = preferences.get("target_savings_rate", 0.2)  # 20% default
        risk_tolerance = preferences.get("risk_tolerance", "medium")
        
        # Calculate target savings and spendable amount
        target_savings = total_income * target_savings_rate
        spendable_budget = total_income - target_savings
        
        # Use RL agent if available
        try:
            from models.rl_agent import get_rl_agent
            
            financial_data = {
                "avg_income": total_income,
                "income_std": total_income * metrics.get("income_volatility", 0.3),
                "savings_rate": savings_rate / 100,
                "days_since_income": 3,
                "expense_pressure": min(current_expenses / total_income, 1.0) if total_income > 0 else 0.5,
                "emergency_months": 1.5,
                "debt_ratio": 0.0,
                "overspend_freq": 0.2,
                "seasonal_factor": 0.5,
                "goal_progress": 0.3,
            }
            
            rl_agent = get_rl_agent()
            budget_allocation = rl_agent.recommend_budget(
                financial_data,
                total_budget=spendable_budget,
                risk_tolerance=risk_tolerance
            )
            
            explanations = rl_agent.explain_recommendation(budget_allocation, financial_data)
            
        except Exception as e:
            self.log(f"RL agent unavailable, using rule-based allocation: {e}", "WARNING")
            budget_allocation = self._rule_based_allocation(spendable_budget)
            explanations = ["Rule-based allocation applied"]
        
        # Generate AI recommendations
        optimization_prompt = f"""Review and enhance this budget allocation:

INCOME: ₹{total_income:.2f}
TARGET SAVINGS: ₹{target_savings:.2f} ({target_savings_rate*100:.0f}%)
SPENDABLE BUDGET: ₹{spendable_budget:.2f}

PROPOSED ALLOCATION:
{self._format_budget(budget_allocation)}

CURRENT SITUATION:
- Current savings rate: {savings_rate:.1f}%
- Income volatility: {metrics.get('income_volatility', 0):.2f}
- Cash flow: ₹{metrics.get('net_cash_flow', 0):.2f}

Provide:
1. Overall budget assessment (is it realistic and achievable?)
2. Specific adjustments to improve savings (3-4 suggestions)
3. Categories where spending can be reduced
4. Emergency fund recommendation

Format as JSON with keys: assessment, adjustments (array), reduction_opportunities (array), emergency_fund_amount"""
        
        response = self.invoke_llm(optimization_prompt)
        ai_recommendations = self.extract_json(response)
        
        if not ai_recommendations:
            ai_recommendations = self._fallback_recommendations(budget_allocation, metrics)
        
        state["budget_recommendation"] = {
            "budget_allocation": budget_allocation,
            "target_savings": target_savings,
            "spendable_budget": spendable_budget,
            "ai_recommendations": ai_recommendations,
            "rl_explanations": explanations,
            "confidence": 0.8
        }
        
        self.log(f"Budget optimized: ₹{spendable_budget:.2f} allocated across {len(budget_allocation)} categories")
        
        return state
    
    def _rule_based_allocation(self, total_budget: float) -> Dict[str, float]:
        """
        Fallback rule-based budget allocation using 50/30/20 principle adapted for gig workers
        """
        return {
            "food_groceries": total_budget * 0.25,  # 25% - Essential
            "rent_utilities": total_budget * 0.30,   # 30% - Essential
            "transportation": total_budget * 0.10,   # 10%
            "healthcare": total_budget * 0.08,       # 8%
            "entertainment": total_budget * 0.10,    # 10%
            "personal_care": total_budget * 0.05,    # 5%
            "education": total_budget * 0.07,        # 7%
            "miscellaneous": total_budget * 0.05     # 5%
        }
    
    def _format_budget(self, budget: Dict[str, float]) -> str:
        """Format budget for display"""
        lines = []
        total = sum(budget.values())
        
        for category, amount in sorted(budget.items(), key=lambda x: -x[1]):
            pct = (amount / total * 100) if total > 0 else 0
            lines.append(f"- {category}: ₹{amount:.2f} ({pct:.1f}%)")
        
        return "\n".join(lines)
    
    def _fallback_recommendations(self, budget: Dict, metrics: Dict) -> Dict:
        """Generate fallback recommendations"""
        total_budget = sum(budget.values())
        
        # Check if savings rate is good
        savings_rate = metrics.get("savings_rate", 0)
        
        if savings_rate >= 15:
            assessment = "Good budget allocation with healthy savings rate"
        else:
            assessment = "Budget needs optimization to increase savings"
        
        adjustments = []
        if savings_rate < 15:
            adjustments.append("Reduce discretionary spending by 10% to boost savings")
            adjustments.append("Look for cheaper alternatives for recurring expenses")
        
        adjustments.append("Set up automatic savings transfer on income days")
        adjustments.append("Track daily expenses to identify leakage")
        
        # Identify high-spending categories
        reduction_opportunities = []
        sorted_budget = sorted(budget.items(), key=lambda x: -x[1])
        
        if len(sorted_budget) >= 3:
            for cat, amount in sorted_budget[2:5]:  # 3rd-5th highest
                if amount > total_budget * 0.15:  # If > 15%
                    reduction_opportunities.append(f"Review {cat} spending (₹{amount:.2f})")
        
        if not reduction_opportunities:
            reduction_opportunities.append("All categories seem reasonable")
        
        # Emergency fund
        monthly_expenses = metrics.get("total_expenses", 0)
        emergency_fund = monthly_expenses * 3  # 3 months
        
        return {
            "assessment": assessment,
            "adjustments": adjustments,
            "reduction_opportunities": reduction_opportunities,
            "emergency_fund_amount": emergency_fund
        }
