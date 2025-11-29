"""
SQLAlchemy Models for MySQL Database
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, JSON, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
from database.mysql_config import Base
import enum

# Enums
class WorkType(str, enum.Enum):
    FREELANCER = "freelancer"
    GIG_WORKER = "gig_worker"
    CONTRACTOR = "contractor"
    PART_TIME = "part_time"
    SELF_EMPLOYED = "self_employed"

class IncomeStability(str, enum.Enum):
    VERY_STABLE = "very_stable"
    MOSTLY_STABLE = "mostly_stable"
    VARIABLE = "variable"
    VERY_VARIABLE = "very_variable"

class RiskTolerance(str, enum.Enum):
    VERY_CONSERVATIVE = "very_conservative"
    CONSERVATIVE = "conservative"
    MODERATE = "moderate"
    AGGRESSIVE = "aggressive"

class TransactionType(str, enum.Enum):
    INCOME = "income"
    EXPENSE = "expense"

# Models
class User(Base):
    """User account model"""
    __tablename__ = "users"
    
    id = Column(String(50), primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Onboarding status
    onboarding_completed = Column(Boolean, default=False)
    
    # Profile data
    work_type = Column(String(50), nullable=True)
    income_stability = Column(String(50), nullable=True)
    monthly_income = Column(Integer, nullable=True)
    monthly_expenses = Column(Integer, nullable=True)
    financial_goals = Column(JSON, nullable=True)
    biggest_challenge = Column(String(50), nullable=True)
    current_savings = Column(String(50), nullable=True)
    budget_experience = Column(String(50), nullable=True)
    risk_tolerance = Column(String(50), nullable=True)
    notification_preferences = Column(String(50), nullable=True)
    
    # Relationships
    transactions = relationship("Transaction", back_populates="user", cascade="all, delete-orphan")
    budgets = relationship("Budget", back_populates="user", cascade="all, delete-orphan")
    forecasts = relationship("Forecast", back_populates="user", cascade="all, delete-orphan")

class Transaction(Base):
    """Financial transaction model"""
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(String(50), ForeignKey("users.id"), nullable=False, index=True)
    
    # Transaction details
    amount = Column(Float, nullable=False)
    type = Column(String(20), nullable=False)  # 'income' or 'expense'
    category = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    date = Column(DateTime, nullable=False, index=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    is_recurring = Column(Boolean, default=False)
    tags = Column(JSON, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="transactions")

class Budget(Base):
    """Budget allocation model"""
    __tablename__ = "budgets"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(String(50), ForeignKey("users.id"), nullable=False, index=True)
    
    # Budget details
    category = Column(String(100), nullable=False)
    allocated_amount = Column(Float, nullable=False)
    spent_amount = Column(Float, default=0.0)
    period = Column(String(20), default="monthly")  # 'weekly', 'monthly', 'yearly'
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    user = relationship("User", back_populates="budgets")

class Forecast(Base):
    """Income/expense forecast model"""
    __tablename__ = "forecasts"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(String(50), ForeignKey("users.id"), nullable=False, index=True)
    
    # Forecast details
    forecast_type = Column(String(20), nullable=False)  # 'income' or 'expense'
    forecast_date = Column(DateTime, nullable=False, index=True)
    predicted_amount = Column(Float, nullable=False)
    confidence_lower = Column(Float, nullable=True)
    confidence_upper = Column(Float, nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    model_version = Column(String(50), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="forecasts")

class AIInsight(Base):
    """AI-generated insights and recommendations"""
    __tablename__ = "ai_insights"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(String(50), ForeignKey("users.id"), nullable=False, index=True)
    
    # Insight details
    insight_type = Column(String(50), nullable=False)  # 'recommendation', 'alert', 'tip'
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    priority = Column(String(20), default="medium")  # 'low', 'medium', 'high', 'urgent'
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    is_read = Column(Boolean, default=False)
    is_dismissed = Column(Boolean, default=False)
    feedback = Column(String(20), nullable=True)  # 'helpful', 'not_helpful'
    
    # Relationships
    user = relationship("User")

class AgentAnalysis(Base):
    """Store complete agent analysis results"""
    __tablename__ = "agent_analyses"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(String(50), ForeignKey("users.id"), nullable=False, index=True)
    
    # Analysis metadata
    analysis_date = Column(DateTime, default=datetime.utcnow, index=True)
    health_score = Column(Float, nullable=True)
    risk_level = Column(String(20), nullable=True)
    
    # Complete analysis data (stored as JSON)
    executive_summary = Column(JSON, nullable=True)
    financial_overview = Column(JSON, nullable=True)
    budget_plan = Column(JSON, nullable=True)
    risk_assessment = Column(JSON, nullable=True)
    savings_strategy = Column(JSON, nullable=True)
    monitoring_alerts = Column(JSON, nullable=True)
    
    # Relationships
    user = relationship("User")
