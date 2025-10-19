# backend/models/rl_agent.py
"""
Reinforcement Learning Agent for Budget Optimization
Uses a simplified Q-learning approach to recommend budget allocations
"""

import torch
import torch.nn as nn
import numpy as np
from typing import Dict, List, Tuple, Optional
import json
import os


class BudgetPolicyNetwork(nn.Module):
    """Neural network for budget allocation policy"""
    
    def __init__(self, state_dim: int = 10, action_dim: int = 8, hidden_dim: int = 64):
        super().__init__()
        self.network = nn.Sequential(
            nn.Linear(state_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, action_dim),
            nn.Softmax(dim=-1)  # Probabilities for budget allocation
        )
    
    def forward(self, state):
        return self.network(state)


class RLAgent:
    """
    Reinforcement Learning Agent for personalized budget optimization
    
    Features:
    - Learns optimal budget allocations based on user's spending patterns
    - Adapts to income volatility
    - Maximizes savings while maintaining essential expenses
    """
    
    DEFAULT_CATEGORIES = [
        "food_groceries",
        "transport",
        "utilities",
        "healthcare",
        "entertainment",
        "education",
        "savings",
        "miscellaneous"
    ]
    
    def __init__(self, model_path: Optional[str] = None):
        self.state_dim = 10  # Features: avg_income, volatility, past_savings, etc.
        self.action_dim = len(self.DEFAULT_CATEGORIES)
        self.policy_net = BudgetPolicyNetwork(self.state_dim, self.action_dim)
        self.optimizer = torch.optim.Adam(self.policy_net.parameters(), lr=0.001)
        
        if model_path and os.path.exists(model_path):
            self.load_model(model_path)
    
    def extract_state(self, financial_data: Dict) -> np.ndarray:
        """
        Extract state vector from user's financial data
        
        State features:
        1. Average monthly income (normalized)
        2. Income volatility (std/mean)
        3. Current savings rate
        4. Days since last income
        5. Upcoming expense pressure
        6. Emergency fund coverage (months)
        7. Debt ratio
        8. Historical overspending frequency
        9. Seasonal income factor
        10. Goal proximity (0-1)
        """
        state = np.zeros(self.state_dim, dtype=np.float32)
        
        # Feature 1: Normalized average income
        avg_income = financial_data.get('avg_income', 30000)
        state[0] = min(avg_income / 100000, 1.0)  # Cap at 100k for normalization
        
        # Feature 2: Income volatility
        income_std = financial_data.get('income_std', 5000)
        state[1] = min((income_std / avg_income) if avg_income > 0 else 0.5, 1.0)
        
        # Feature 3: Current savings rate
        state[2] = financial_data.get('savings_rate', 0.1)
        
        # Feature 4: Days since last income (normalized to 0-1, max 30 days)
        state[3] = min(financial_data.get('days_since_income', 7) / 30, 1.0)
        
        # Feature 5: Upcoming expense pressure (ratio of pending bills to available cash)
        state[4] = min(financial_data.get('expense_pressure', 0.3), 1.0)
        
        # Feature 6: Emergency fund (months of expenses covered)
        state[5] = min(financial_data.get('emergency_months', 1.0) / 6, 1.0)
        
        # Feature 7: Debt ratio
        state[6] = min(financial_data.get('debt_ratio', 0.0), 1.0)
        
        # Feature 8: Overspending frequency (0-1)
        state[7] = financial_data.get('overspend_freq', 0.2)
        
        # Feature 9: Seasonal factor (gig work seasonality)
        state[8] = financial_data.get('seasonal_factor', 0.5)
        
        # Feature 10: Goal proximity
        state[9] = financial_data.get('goal_progress', 0.0)
        
        return state
    
    def recommend_budget(
        self, 
        financial_data: Dict, 
        total_budget: float,
        risk_tolerance: str = "medium"
    ) -> Dict[str, float]:
        """
        Generate optimized budget allocation using the policy network
        
        Args:
            financial_data: User's financial metrics
            total_budget: Total amount to allocate
            risk_tolerance: "low", "medium", or "high"
        
        Returns:
            Dictionary mapping category to allocated amount
        """
        state = self.extract_state(financial_data)
        state_tensor = torch.FloatTensor(state).unsqueeze(0)
        
        with torch.no_grad():
            allocation_probs = self.policy_net(state_tensor).squeeze().numpy()
        
        # Adjust based on risk tolerance
        allocation_probs = self._adjust_for_risk(allocation_probs, risk_tolerance)
        
        # Ensure minimum allocations for essentials
        allocation_probs = self._enforce_essential_minimums(allocation_probs, financial_data)
        
        # Normalize to sum to 1
        allocation_probs = allocation_probs / allocation_probs.sum()
        
        # Convert to actual amounts
        budget_allocation = {
            category: float(prob * total_budget)
            for category, prob in zip(self.DEFAULT_CATEGORIES, allocation_probs)
        }
        
        return budget_allocation
    
    def _adjust_for_risk(self, probs: np.ndarray, risk_tolerance: str) -> np.ndarray:
        """Adjust allocations based on risk tolerance"""
        adjusted = probs.copy()
        
        # Get index of savings category
        savings_idx = self.DEFAULT_CATEGORIES.index("savings")
        
        if risk_tolerance == "low":
            # Increase savings, reduce entertainment
            adjusted[savings_idx] *= 1.3
            ent_idx = self.DEFAULT_CATEGORIES.index("entertainment")
            adjusted[ent_idx] *= 0.7
        
        elif risk_tolerance == "high":
            # More flexible with entertainment, lower savings
            adjusted[savings_idx] *= 0.8
            ent_idx = self.DEFAULT_CATEGORIES.index("entertainment")
            adjusted[ent_idx] *= 1.2
        
        return adjusted
    
    def _enforce_essential_minimums(
        self, 
        probs: np.ndarray, 
        financial_data: Dict
    ) -> np.ndarray:
        """Ensure essential categories get minimum allocation"""
        adjusted = probs.copy()
        
        # Essential categories with minimum % allocations
        essentials = {
            "food_groceries": 0.20,  # At least 20%
            "utilities": 0.10,       # At least 10%
            "healthcare": 0.05,      # At least 5%
            "savings": 0.10,         # At least 10%
        }
        
        for category, min_pct in essentials.items():
            idx = self.DEFAULT_CATEGORIES.index(category)
            if adjusted[idx] < min_pct:
                deficit = min_pct - adjusted[idx]
                adjusted[idx] = min_pct
                
                # Reduce from non-essential categories
                non_essential = ["entertainment", "miscellaneous"]
                for ne_cat in non_essential:
                    ne_idx = self.DEFAULT_CATEGORIES.index(ne_cat)
                    reduction = min(adjusted[ne_idx] * 0.5, deficit / len(non_essential))
                    adjusted[ne_idx] -= reduction
                    deficit -= reduction
                    if deficit <= 0:
                        break
        
        return adjusted
    
    def explain_recommendation(
        self, 
        budget_allocation: Dict[str, float],
        financial_data: Dict
    ) -> List[str]:
        """Generate human-readable explanations for budget recommendations"""
        explanations = []
        
        total = sum(budget_allocation.values())
        
        # Savings explanation
        savings_pct = (budget_allocation.get("savings", 0) / total) * 100
        if savings_pct >= 20:
            explanations.append(
                f"✅ Excellent {savings_pct:.1f}% savings allocation builds your financial cushion"
            )
        elif savings_pct >= 10:
            explanations.append(
                f"💰 {savings_pct:.1f}% to savings is a solid start. Aim for 15-20% over time."
            )
        else:
            explanations.append(
                f"⚠️ Only {savings_pct:.1f}% savings. Try reducing discretionary spending."
            )
        
        # Income volatility consideration
        volatility = financial_data.get('income_std', 0) / max(financial_data.get('avg_income', 1), 1)
        if volatility > 0.3:
            explanations.append(
                "📊 High income variability detected - prioritized emergency fund building"
            )
        
        # Food budget check
        food_pct = (budget_allocation.get("food_groceries", 0) / total) * 100
        if food_pct < 15:
            explanations.append(
                f"🍽️ Food budget at {food_pct:.1f}% - ensure adequate nutrition"
            )
        
        # Entertainment check
        ent_pct = (budget_allocation.get("entertainment", 0) / total) * 100
        if ent_pct > 15:
            explanations.append(
                f"🎭 Entertainment at {ent_pct:.1f}% - consider if this aligns with your goals"
            )
        
        return explanations
    
    def train_step(
        self, 
        state: np.ndarray, 
        action: np.ndarray, 
        reward: float
    ) -> float:
        """
        Single training step (simplified policy gradient)
        
        Args:
            state: Current financial state
            action: Budget allocation taken
            reward: Outcome (e.g., savings achieved, goals met)
        
        Returns:
            Loss value
        """
        state_tensor = torch.FloatTensor(state).unsqueeze(0)
        action_tensor = torch.FloatTensor(action).unsqueeze(0)
        
        # Forward pass
        predicted_action = self.policy_net(state_tensor)
        
        # Policy gradient loss (simplified)
        loss = -torch.sum(predicted_action * action_tensor) * reward
        
        # Backward pass
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()
        
        return loss.item()
    
    def save_model(self, path: str):
        """Save model weights"""
        torch.save({
            'policy_net_state_dict': self.policy_net.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
        }, path)
    
    def load_model(self, path: str):
        """Load model weights"""
        checkpoint = torch.load(path, weights_only=True)
        self.policy_net.load_state_dict(checkpoint['policy_net_state_dict'])
        self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
    
    def calculate_expected_savings(
        self, 
        budget_allocation: Dict[str, float],
        historical_spending: Optional[Dict[str, float]] = None
    ) -> float:
        """
        Estimate expected savings based on recommended budget vs historical spending
        
        Args:
            budget_allocation: Recommended budget
            historical_spending: Past average spending per category
        
        Returns:
            Expected monthly savings
        """
        if not historical_spending:
            # If no history, return the allocated savings amount
            return budget_allocation.get("savings", 0)
        
        # Calculate savings from reducing overspending
        total_reduction = 0
        for category, allocated in budget_allocation.items():
            if category == "savings":
                continue
            historical = historical_spending.get(category, allocated)
            if historical > allocated:
                total_reduction += (historical - allocated)
        
        # Expected savings = allocated savings + reductions from overspending
        return budget_allocation.get("savings", 0) + (total_reduction * 0.7)  # 70% success rate


# Singleton instance for the application
_rl_agent_instance = None

def get_rl_agent() -> RLAgent:
    """Get or create the RL agent singleton"""
    global _rl_agent_instance
    if _rl_agent_instance is None:
        model_path = os.getenv("RL_MODEL_PATH", "models/rl_budget_agent.pth")
        _rl_agent_instance = RLAgent(model_path)
    return _rl_agent_instance
