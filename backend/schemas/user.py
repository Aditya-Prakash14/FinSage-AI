# backend/schemas/user.py

from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional


class UserCreate(BaseModel):
    """Create a new user"""
    email: EmailStr
    name: str = Field(..., min_length=1, max_length=100)
    phone: Optional[str] = Field(None, pattern=r'^\+?[1-9]\d{9,14}$')
    primary_income_source: Optional[str] = None
    occupation: Optional[str] = None


class User(UserCreate):
    """User with metadata"""
    id: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = True
    
    class Config:
        from_attributes = True


class FinancialGoal(BaseModel):
    """Savings or financial goal"""
    id: str
    user_id: str
    goal_name: str
    target_amount: float = Field(..., gt=0)
    current_amount: float = Field(default=0.0, ge=0)
    deadline: Optional[datetime] = None
    priority: int = Field(default=1, ge=1, le=5)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class FinancialGoalCreate(BaseModel):
    """Create a financial goal"""
    user_id: str
    goal_name: str
    target_amount: float = Field(..., gt=0)
    deadline: Optional[datetime] = None
    priority: int = Field(default=1, ge=1, le=5)
