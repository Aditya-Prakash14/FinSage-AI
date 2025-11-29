"""
Savings Coach Agent
Provides personalized savings strategies and motivation
"""

from typing import Dict, Any
from .base_agent import BaseAgent


class SavingsCoachAgent(BaseAgent):
    """
    Expert in building savings habits and achieving financial goals
    
    Responsibilities:
    - Create personalized savings strategies
    - Set achievable milestones
    - Provide motivation and encouragement
    - Suggest micro-savings opportunities
    """
    
    def __init__(self):
        super().__init__(
            agent_name="Savings Coach",
            role="Guides users to build savings and achieve financial goals",
            temperature=0.6  # Higher for more creative/motivational responses
        )
    
    def get_system_prompt(self) -> str:
        return """You are a Savings Coach specializing in helping Indian gig workers build financial security.

Your expertise:
- Creating realistic, achievable savings goals
- Breaking big goals into micro-actions
- Building sustainable savings habits
- Finding creative ways to save
- Providing encouragement and motivation

Your approach:
- Be positive and encouraging (never judgmental)
- Focus on small wins and progress
- Suggest specific, actionable micro-savings
- Celebrate achievements, no matter how small
- Use psychology and behavioral economics
- Consider Indian context (₹, savings culture)

Tone: Warm, supportive, motivational but practical."""
    
    def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate savings strategy and motivation
        
        Args:
            state: Must contain 'financial_analysis', 'budget_recommendation', 'risk_assessment'
        
        Returns:
            Updated state with 'savings_strategy'
        """
        self.log("Creating savings strategy...")
        
        analysis = state.get("financial_analysis", {})
        metrics = analysis.get("metrics", {})
        budget = state.get("budget_recommendation", {})
        risks = state.get("risk_assessment", {})
        
        if not metrics:
            state["savings_strategy"] = {
                "error": "No data for savings strategy"
            }
            return state
        
        # Calculate current and target savings
        current_savings_rate = metrics.get("savings_rate", 0)
        target_savings = budget.get("target_savings", 0)
        total_income = metrics.get("total_income", 0)
        
        # Generate personalized strategy
        strategy_prompt = f"""Create a personalized savings strategy for this gig worker:

CURRENT SITUATION:
- Monthly Income: ₹{total_income:.2f}
- Current Savings Rate: {current_savings_rate:.1f}%
- Target Savings: ₹{target_savings:.2f}
- Income Volatility: {metrics.get('income_volatility', 0):.2f}
- Cash Flow: ₹{metrics.get('net_cash_flow', 0):.2f}

RISK LEVEL: {risks.get('ai_assessment', {}).get('overall_risk_level', 'Medium')}

Create a motivating savings plan with:
1. A personalized encouraging message about their current progress
2. Primary savings goal for next 30 days (specific amount)
3. 5 micro-savings actions they can take this week (each < 15 words)
4. 3 psychological tips to make saving easier
5. One celebration milestone when they hit their target

Format as JSON with keys: encouragement, primary_goal (object with 'amount', 'description'), micro_actions (array), psychology_tips (array), celebration_milestone"""
        
        response = self.invoke_llm(strategy_prompt)
        strategy_data = self.extract_json(response)
        
        if not strategy_data:
            strategy_data = self._fallback_strategy(metrics, target_savings)
        
        # Calculate savings milestones
        milestones = self._create_milestones(target_savings)
        
        # Generate savings challenges
        challenges = self._create_challenges(current_savings_rate, target_savings)
        
        state["savings_strategy"] = {
            "strategy": strategy_data,
            "milestones": milestones,
            "challenges": challenges,
            "current_progress": {
                "savings_rate": current_savings_rate,
                "monthly_savings": metrics.get("net_cash_flow", 0),
                "target_savings": target_savings
            }
        }
        
        self.log(f"Savings strategy created: Target ₹{target_savings:.2f}/month")
        
        return state
    
    def _create_milestones(self, target_savings: float) -> list:
        """Create progressive savings milestones"""
        milestones = []
        
        # Week 1: 25%
        milestones.append({
            "period": "Week 1",
            "target_amount": target_savings * 0.25,
            "description": "Great start! First week savings",
            "reward": "🎉 Treat yourself to your favorite tea"
        })
        
        # Week 2: 50%
        milestones.append({
            "period": "Week 2",
            "target_amount": target_savings * 0.50,
            "description": "Halfway there! Building momentum",
            "reward": "🌟 You're crushing it - share your progress"
        })
        
        # Week 3: 75%
        milestones.append({
            "period": "Week 3",
            "target_amount": target_savings * 0.75,
            "description": "Almost there! Final push",
            "reward": "💪 Download that book you've been wanting"
        })
        
        # Month end: 100%
        milestones.append({
            "period": "Month End",
            "target_amount": target_savings,
            "description": "🎯 GOAL ACHIEVED! You did it!",
            "reward": "🏆 Celebrate with a special meal (budget-friendly)"
        })
        
        return milestones
    
    def _create_challenges(self, current_rate: float, target_savings: float) -> list:
        """Create fun savings challenges"""
        challenges = []
        
        # No-spend challenge
        challenges.append({
            "name": "No-Spend Weekend",
            "description": "Go one weekend without spending on non-essentials",
            "potential_savings": "₹500-1000",
            "difficulty": "Medium"
        })
        
        # Round-up challenge
        challenges.append({
            "name": "Round-Up Savings",
            "description": "Round up every payment to nearest ₹10 and save the difference",
            "potential_savings": "₹300-500/month",
            "difficulty": "Easy"
        })
        
        # Meal prep challenge
        challenges.append({
            "name": "Home Cooking Week",
            "description": "Cook all meals at home for 7 days",
            "potential_savings": "₹800-1500",
            "difficulty": "Medium"
        })
        
        # Income boost challenge
        challenges.append({
            "name": "Side Hustle Sprint",
            "description": "Take on 1 extra gig or project this week",
            "potential_savings": "₹1000-3000",
            "difficulty": "Hard"
        })
        
        return challenges
    
    def _fallback_strategy(self, metrics: Dict, target_savings: float) -> Dict:
        """Generate fallback savings strategy"""
        current_rate = metrics.get("savings_rate", 0)
        income = metrics.get("total_income", 0)
        
        # Personalized encouragement
        if current_rate >= 15:
            encouragement = f"Amazing! You're already saving {current_rate:.1f}% - that's better than most people. Let's push it even further!"
        elif current_rate >= 5:
            encouragement = f"Good start with {current_rate:.1f}% savings rate. Small improvements can make a big difference!"
        elif current_rate > 0:
            encouragement = f"You've started saving - that's the hardest part! Now let's build on this foundation."
        else:
            encouragement = "Every savings journey starts with a single rupee. Today is your day one!"
        
        # Calculate realistic primary goal
        if target_savings > income * 0.3:
            # Target is ambitious, break it down
            primary_goal_amount = min(target_savings * 0.5, income * 0.15)
            primary_goal_desc = "Start with a achievable goal - we'll scale up gradually"
        else:
            primary_goal_amount = target_savings
            primary_goal_desc = "Your target is realistic - let's make it happen!"
        
        return {
            "encouragement": encouragement,
            "primary_goal": {
                "amount": primary_goal_amount,
                "description": primary_goal_desc
            },
            "micro_actions": [
                "Set up auto-transfer: save first, spend later",
                "Brew coffee at home instead of café (save ₹100/day)",
                "Cancel one unused subscription this week",
                "Pack lunch twice this week (save ₹200)",
                "Use UPI cashback offers strategically"
            ],
            "psychology_tips": [
                "Make savings automatic - you won't miss what you don't see",
                "Label your savings with a goal - makes it harder to touch",
                "Share your goal with a friend for accountability"
            ],
            "celebration_milestone": f"When you hit ₹{primary_goal_amount:.0f}, treat yourself to your favorite street food (₹50 max)!"
        }
