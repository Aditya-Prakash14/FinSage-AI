# backend/schemas/forecast.py

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class ForecastPoint(BaseModel):
    """Single forecasted data point"""
    date: datetime
    predicted_value: float
    lower_bound: Optional[float] = None
    upper_bound: Optional[float] = None
    confidence: Optional[float] = Field(None, ge=0, le=1)


class ForecastRequest(BaseModel):
    """Request for income/expense forecast"""
    user_id: str
    forecast_days: int = Field(default=7, ge=1, le=90, description="Number of days to forecast")
    include_confidence_intervals: bool = Field(default=True)


class ForecastResponse(BaseModel):
    """Forecast results"""
    income_forecast: list[ForecastPoint]
    expense_forecast: list[ForecastPoint]
    net_cash_flow: list[dict]  # [{date, net_flow}]
    volatility_score: Optional[float] = Field(None, description="Income volatility (0-1)")
    risk_level: Optional[str] = Field(None, description="low, medium, high")
    recommended_actions: list[str]
    generated_at: datetime = Field(default_factory=datetime.utcnow)


class InsightRequest(BaseModel):
    """Request for AI-generated financial insights"""
    user_id: str
    context: Optional[str] = Field(None, description="Additional context for personalized advice")


class InsightResponse(BaseModel):
    """AI-generated insights and recommendations"""
    summary: str
    insights: list[str]
    action_items: list[str]
    warnings: list[str]
    confidence_score: float = Field(..., ge=0, le=1)
