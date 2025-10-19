# backend/schemas/budget.py

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class BudgetCategory(BaseModel):
    """Budget allocation per category"""
    category: str
    allocated_amount: float = Field(..., gt=0)
    spent_amount: float = Field(default=0.0)
    remaining: Optional[float] = None
    
    def calculate_remaining(self):
        self.remaining = self.allocated_amount - self.spent_amount


class BudgetCreate(BaseModel):
    """Create a new budget"""
    user_id: str
    period: str = Field(default="monthly", pattern="^(weekly|monthly|quarterly)$")
    categories: list[BudgetCategory]
    total_budget: float = Field(..., gt=0)


class Budget(BudgetCreate):
    """Budget with metadata"""
    id: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = True


class BudgetOptimizationRequest(BaseModel):
    """Request RL-based budget optimization"""
    user_id: str
    target_savings_rate: float = Field(default=0.15, ge=0, le=0.5, description="Desired savings rate (0-50%)")
    risk_tolerance: str = Field(default="medium", pattern="^(low|medium|high)$")


class BudgetOptimizationResponse(BaseModel):
    """RL-optimized budget recommendations"""
    optimized_categories: list[BudgetCategory]
    expected_savings: float
    confidence: float = Field(..., ge=0, le=1)
    reasoning: str
    adjustments_made: list[str]
