# backend/routes/finance_routes.py
"""
Comprehensive finance API routes for FinSage AI
"""

from fastapi import APIRouter, HTTPException, Depends, Body
from typing import List, Dict, Optional
from datetime import datetime, timedelta

from schemas.forecast import ForecastRequest, ForecastResponse, InsightRequest, InsightResponse, ForecastPoint
from schemas.budget import BudgetCreate, BudgetOptimizationRequest, BudgetOptimizationResponse, BudgetCategory
from schemas.transaction import TransactionCreate, Transaction, TransactionBatch
from schemas.user import UserCreate, User, FinancialGoalCreate, FinancialGoal

from models.income_predictor import predict_income
from models.expense_predictor import predict_expense
from models.rl_agent import get_rl_agent
from models.ai_advisor import get_advisor

from database.mongo_config import get_db
from database.repositories import RepositoryFactory
from utils.privacy import mask_sensitive_data, create_audit_log, sanitize_amount

router = APIRouter()


# ==================== Forecast Endpoints ====================

@router.post("/forecast", response_model=ForecastResponse, tags=["Forecasting"])
async def generate_forecast(
    user_id: str = Body(..., embed=True),
    forecast_days: int = Body(7, embed=True),
    include_confidence: bool = Body(True, embed=True),
    db=Depends(get_db)
):
    """
    Generate income and expense forecasts with AI-powered insights
    
    - Uses Prophet for time-series prediction
    - Calculates volatility and risk metrics
    - Provides AI-generated actionable recommendations
    """
    repo_factory = RepositoryFactory(db)
    txn_repo = repo_factory.get_transaction_repo()
    
    # Get recent transactions (last 90 days for better predictions)
    transactions = txn_repo.get_recent_transactions(user_id, days=90)
    
    if not transactions:
        raise HTTPException(status_code=404, detail="No transaction history found for this user")
    
    # Convert MongoDB documents to dict list
    txn_list = []
    for txn in transactions:
        txn_list.append({
            "date": txn["date"].isoformat() if isinstance(txn["date"], datetime) else txn["date"],
            "amount": txn["amount"],
            "type": txn["type"],
            "category": txn.get("category"),
        })
    
    # Generate predictions
    income_forecast = predict_income(txn_list, forecast_days, include_confidence)
    expense_forecast = predict_expense(txn_list, forecast_days, include_confidence)
    
    # Calculate net cash flow
    net_cash_flow = []
    for i in range(len(income_forecast.get("forecast", []))):
        inc_point = income_forecast["forecast"][i]
        exp_point = expense_forecast["forecast"][i]
        net_cash_flow.append({
            "date": inc_point["date"],
            "net_flow": inc_point["predicted_value"] - exp_point["predicted_value"]
        })
    
    # Get AI-generated insights
    advisor = get_advisor()
    insights = advisor.generate_forecast_insights(income_forecast, expense_forecast)
    
    # Build response
    response = ForecastResponse(
        income_forecast=[ForecastPoint(**p) for p in income_forecast.get("forecast", [])],
        expense_forecast=[ForecastPoint(**p) for p in expense_forecast.get("forecast", [])],
        net_cash_flow=net_cash_flow,
        volatility_score=income_forecast.get("volatility_score"),
        risk_level=income_forecast.get("risk_level"),
        recommended_actions=insights.get("action_items", []),
    )
    
    # Audit log
    create_audit_log("forecast_generated", user_id, "forecast", {"days": forecast_days})
    
    return response


@router.post("/insights", response_model=InsightResponse, tags=["AI Insights"])
async def generate_insights(request: InsightRequest, db=Depends(get_db)):
    """
    Generate comprehensive AI-powered financial insights
    
    - Analyzes spending patterns
    - Identifies savings opportunities
    - Provides personalized recommendations
    """
    repo_factory = RepositoryFactory(db)
    txn_repo = repo_factory.get_transaction_repo()
    
    transactions = txn_repo.get_recent_transactions(request.user_id, days=30)
    
    if not transactions:
        raise HTTPException(status_code=404, detail="Insufficient data for insights")
    
    # Prepare transaction data
    txn_list = [
        {
            "date": txn["date"].isoformat() if isinstance(txn["date"], datetime) else txn["date"],
            "amount": txn["amount"],
            "type": txn["type"],
            "category": txn.get("category"),
        }
        for txn in transactions
    ]
    
    # Generate forecasts for context
    income_forecast = predict_income(txn_list, forecast_days=7, include_confidence=False)
    expense_forecast = predict_expense(txn_list, forecast_days=7, include_confidence=False)
    
    # Get AI insights
    advisor = get_advisor()
    user_context = {"note": request.context} if request.context else None
    insights_data = advisor.generate_forecast_insights(
        income_forecast, 
        expense_forecast, 
        user_context
    )
    
    response = InsightResponse(
        summary=insights_data.get("summary", "Analysis complete"),
        insights=insights_data.get("insights", []),
        action_items=insights_data.get("action_items", []),
        warnings=insights_data.get("warnings", []),
        confidence_score=insights_data.get("confidence_score", 0.7)
    )
    
    create_audit_log("insights_generated", request.user_id, "insights")
    
    return response


# ==================== Budget Endpoints ====================

@router.post("/budget/optimize", response_model=BudgetOptimizationResponse, tags=["Budget"])
async def optimize_budget(request: BudgetOptimizationRequest, db=Depends(get_db)):
    """
    Use RL agent to optimize budget allocation
    
    - Learns from spending patterns
    - Recommends category-wise allocations
    - Maximizes savings potential
    """
    repo_factory = RepositoryFactory(db)
    txn_repo = repo_factory.get_transaction_repo()
    
    # Get recent transaction data
    transactions = txn_repo.get_recent_transactions(request.user_id, days=60)
    
    if not transactions:
        raise HTTPException(status_code=404, detail="No transaction history for budget optimization")
    
    # Calculate financial metrics for RL agent
    txn_list = [
        {"date": txn["date"], "amount": txn["amount"], "type": txn["type"]}
        for txn in transactions
    ]
    
    income_forecast = predict_income(txn_list, forecast_days=30, include_confidence=False)
    expense_forecast = predict_expense(txn_list, forecast_days=30, include_confidence=False)
    
    # Prepare financial data for RL agent
    avg_income = income_forecast.get("avg_daily_income", 0) * 30
    volatility = income_forecast.get("volatility_score", 0.3)
    
    financial_data = {
        "avg_income": avg_income,
        "income_std": avg_income * volatility,
        "savings_rate": request.target_savings_rate,
        "days_since_income": 3,  # Could be calculated from transactions
        "expense_pressure": 0.4,
        "emergency_months": 1.5,
        "debt_ratio": 0.0,
        "overspend_freq": 0.2,
        "seasonal_factor": 0.5,
        "goal_progress": 0.3,
    }
    
    # Get RL-optimized budget
    rl_agent = get_rl_agent()
    budget_allocation = rl_agent.recommend_budget(
        financial_data,
        total_budget=avg_income * (1 - request.target_savings_rate),
        risk_tolerance=request.risk_tolerance
    )
    
    # Get explanations
    explanations = rl_agent.explain_recommendation(budget_allocation, financial_data)
    
    # Calculate expected savings
    historical_spending = expense_forecast.get("category_breakdown", {})
    expected_savings = rl_agent.calculate_expected_savings(budget_allocation, historical_spending)
    
    # Convert to response format
    optimized_categories = [
        BudgetCategory(
            category=cat,
            allocated_amount=amount,
            spent_amount=historical_spending.get(cat, 0)
        )
        for cat, amount in budget_allocation.items()
    ]
    
    response = BudgetOptimizationResponse(
        optimized_categories=optimized_categories,
        expected_savings=expected_savings,
        confidence=0.75,  # RL model confidence
        reasoning="\n".join(explanations),
        adjustments_made=[f"Optimized {cat} allocation" for cat in budget_allocation.keys()]
    )
    
    create_audit_log("budget_optimized", request.user_id, "budget")
    
    return response


@router.post("/budget", tags=["Budget"])
async def create_budget(budget: BudgetCreate, db=Depends(get_db)):
    """Create a new budget for the user"""
    repo_factory = RepositoryFactory(db)
    budget_repo = repo_factory.get_budget_repo()
    
    budget_data = budget.model_dump()
    budget_id = budget_repo.create_budget(budget_data)
    
    create_audit_log("budget_created", budget.user_id, "budget", {"budget_id": budget_id})
    
    return {"budget_id": budget_id, "message": "Budget created successfully"}


# ==================== Transaction Endpoints ====================

@router.post("/transactions", tags=["Transactions"])
async def add_transaction(transaction: TransactionCreate, user_id: str, db=Depends(get_db)):
    """Add a single transaction"""
    repo_factory = RepositoryFactory(db)
    txn_repo = repo_factory.get_transaction_repo()
    
    txn_data = transaction.model_dump()
    txn_data["user_id"] = user_id
    txn_data["amount"] = sanitize_amount(txn_data["amount"])
    
    txn_id = txn_repo.create(txn_data)
    
    create_audit_log("transaction_created", user_id, "transaction", {"txn_id": txn_id})
    
    return {"transaction_id": txn_id, "message": "Transaction added successfully"}


@router.post("/transactions/batch", tags=["Transactions"])
async def add_transactions_batch(batch: TransactionBatch, user_id: str, db=Depends(get_db)):
    """Add multiple transactions at once"""
    repo_factory = RepositoryFactory(db)
    txn_repo = repo_factory.get_transaction_repo()
    
    txn_list = []
    for txn in batch.transactions:
        txn_data = txn.model_dump()
        txn_data["user_id"] = user_id
        txn_data["amount"] = sanitize_amount(txn_data["amount"])
        txn_list.append(txn_data)
    
    txn_ids = txn_repo.batch_create(txn_list)
    
    create_audit_log("batch_transactions_created", user_id, "transaction", {"count": len(txn_ids)})
    
    return {"transaction_ids": txn_ids, "count": len(txn_ids), "message": "Transactions added successfully"}


@router.get("/transactions", tags=["Transactions"])
async def get_transactions(
    user_id: str,
    days: int = 30,
    transaction_type: Optional[str] = None,
    db=Depends(get_db)
):
    """Get user's recent transactions"""
    repo_factory = RepositoryFactory(db)
    txn_repo = repo_factory.get_transaction_repo()
    
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    transactions = txn_repo.find_by_user(
        user_id,
        start_date=cutoff_date,
        transaction_type=transaction_type
    )
    
    # Convert MongoDB ObjectId to string
    for txn in transactions:
        txn["id"] = str(txn.pop("_id"))
    
    return {"transactions": transactions, "count": len(transactions)}


# ==================== Anomaly Detection ====================

@router.get("/anomalies", tags=["Analytics"])
async def detect_anomalies(user_id: str, db=Depends(get_db)):
    """
    Detect unusual spending patterns
    
    - Identifies expenses > 2 std devs from mean
    - Flags category overspending
    - Provides AI explanations
    """
    repo_factory = RepositoryFactory(db)
    txn_repo = repo_factory.get_transaction_repo()
    
    transactions = txn_repo.get_recent_transactions(user_id, days=60)
    
    if len(transactions) < 10:
        return {"anomalies": [], "message": "Insufficient data for anomaly detection"}
    
    # Prepare data
    txn_list = [
        {"date": txn["date"], "amount": abs(txn["amount"]), "category": txn.get("category")}
        for txn in transactions
        if txn["type"] == "debit"
    ]
    
    import pandas as pd
    import numpy as np
    
    df = pd.DataFrame(txn_list)
    
    anomalies = []
    
    # Overall spending anomalies
    mean_amount = df["amount"].mean()
    std_amount = df["amount"].std()
    threshold = mean_amount + (2 * std_amount)
    
    outliers = df[df["amount"] > threshold]
    
    for _, row in outliers.iterrows():
        anomaly_data = {
            "date": row["date"].isoformat() if isinstance(row["date"], datetime) else str(row["date"]),
            "amount": float(row["amount"]),
            "expected": float(mean_amount),
            "deviation_pct": ((row["amount"] - mean_amount) / mean_amount) * 100,
            "category": row.get("category", "Unknown")
        }
        
        # Get AI explanation
        advisor = get_advisor()
        explanation = advisor.analyze_spending_anomaly(anomaly_data)
        
        anomalies.append({
            **anomaly_data,
            "explanation": explanation
        })
    
    return {"anomalies": anomalies, "count": len(anomalies)}


# ==================== Multi-Agent Analysis ====================

@router.post("/agent-analysis", tags=["AI Agents"])
async def run_agent_analysis(
    user_id: str = Body(..., embed=True),
    days: int = Body(30, embed=True),
    target_savings_rate: float = Body(0.2, embed=True),
    risk_tolerance: str = Body("medium", embed=True),
    db=Depends(get_db)
):
    """
    Run comprehensive multi-agent financial analysis using LangGraph
    
    This endpoint coordinates 5 specialized AI agents:
    1. **Financial Analyst** - Analyzes transaction patterns and metrics
    2. **Budget Optimizer** - Creates optimal budget allocation using RL
    3. **Risk Assessor** - Evaluates financial risks and vulnerabilities
    4. **Savings Coach** - Provides personalized savings strategies
    5. **Transaction Monitor** - Detects anomalies and alerts
    
    Returns a comprehensive report with insights from all agents.
    """
    repo_factory = RepositoryFactory(db)
    txn_repo = repo_factory.get_transaction_repo()
    
    # Get transactions
    transactions = txn_repo.get_recent_transactions(user_id, days=days)
    
    if not transactions:
        raise HTTPException(
            status_code=404, 
            detail=f"No transactions found for user {user_id}"
        )
    
    # Convert to list of dicts
    txn_list = []
    for txn in transactions:
        txn_dict = {
            "date": txn["date"].isoformat() if isinstance(txn["date"], datetime) else txn["date"],
            "amount": txn["amount"],
            "type": txn["type"],
            "category": txn.get("category", "miscellaneous"),
            "description": txn.get("description", ""),
            "source": txn.get("source", "")
        }
        txn_list.append(txn_dict)
    
    # User preferences
    user_preferences = {
        "target_savings_rate": target_savings_rate,
        "risk_tolerance": risk_tolerance,
    }
    
    # Run multi-agent analysis
    try:
        from agents.orchestrator import get_orchestrator
        
        orchestrator = get_orchestrator()
        comprehensive_report = orchestrator.analyze(
            user_id=user_id,
            transactions=txn_list,
            user_preferences=user_preferences
        )
        
        # Log the analysis
        create_audit_log("agent_analysis_complete", user_id, "agent_system", {
            "transaction_count": len(txn_list),
            "health_score": comprehensive_report.get("financial_overview", {}).get("health_score")
        })
        
        return comprehensive_report
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Agent analysis failed: {str(e)}"
        )


# ==================== Health Check ====================

@router.get("/health", tags=["System"])
async def health_check():
    """API health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }
