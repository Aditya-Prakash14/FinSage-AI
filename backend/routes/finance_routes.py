# backend/routes/finance_routes.py
"""
Finance API routes for FinSage AI - MySQL version
"""

from fastapi import APIRouter, HTTPException, Depends, Body, Query
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
import secrets

from database.mysql_config import mysql_manager
from database import models

router = APIRouter()

def get_db():
    """Database session dependency"""
    yield from mysql_manager.get_db()

def ensure_user_exists(db: Session, user_id: str):
    """Ensure user exists in database, create if not"""
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        # Create a demo user
        user = models.User(
            id=user_id,
            email=f"{user_id}@demo.finsage.ai",
            password_hash="demo_hash",  # Not used for demo users
            name="Demo User",
            is_demo=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    return user

# ==================== Health Check ====================

@router.get("/health", tags=["System"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }

# ==================== Transaction Endpoints ====================

@router.post("/transactions", tags=["Transactions"])
async def create_transaction(
    payload: Dict = Body(...),
    db: Session = Depends(get_db)
):
    """Create a single transaction"""
    try:
        user_id = payload.get("user_id")
        
        # Ensure user exists
        ensure_user_exists(db, user_id)
        
        transaction = models.Transaction(
            user_id=user_id,
            amount=payload.get("amount"),
            type=payload.get("type"),
            category=payload.get("category"),
            description=payload.get("description"),
            date=datetime.fromisoformat(payload.get("date")) if payload.get("date") else datetime.utcnow()
        )
        db.add(transaction)
        db.commit()
        db.refresh(transaction)
        
        return {
            "success": True,
            "transaction_id": transaction.id,
            "message": "Transaction created successfully"
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/transactions/batch", tags=["Transactions"])
async def create_transactions_batch(
    user_id: str = Query(...),
    transactions: List[Dict] = Body(...),
    db: Session = Depends(get_db)
):
    """Create multiple transactions at once"""
    try:
        # Ensure user exists before creating transactions
        ensure_user_exists(db, user_id)
        
        transaction_ids = []
        for txn_data in transactions:
            transaction = models.Transaction(
                user_id=user_id,
                amount=txn_data.get("amount"),
                type=txn_data.get("type"),
                category=txn_data.get("category"),
                description=txn_data.get("description"),
                date=datetime.fromisoformat(txn_data.get("date")) if txn_data.get("date") else datetime.utcnow()
            )
            db.add(transaction)
            db.flush()
            transaction_ids.append(transaction.id)
        
        db.commit()
        
        return {
            "success": True,
            "transaction_ids": transaction_ids,
            "count": len(transaction_ids),
            "message": f"{len(transaction_ids)} transactions created successfully"
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/transactions", tags=["Transactions"])
async def get_transactions(
    user_id: str = Query(...),
    days: int = Query(30),
    db: Session = Depends(get_db)
):
    """Get user transactions"""
    try:
        start_date = datetime.utcnow() - timedelta(days=days)
        transactions = db.query(models.Transaction).filter(
            models.Transaction.user_id == user_id,
            models.Transaction.date >= start_date
        ).order_by(desc(models.Transaction.date)).all()
        
        return {
            "success": True,
            "count": len(transactions),
            "transactions": [
                {
                    "id": t.id,
                    "amount": t.amount,
                    "type": t.type,
                    "category": t.category,
                    "description": t.description,
                    "date": t.date.isoformat() if t.date else None
                }
                for t in transactions
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================== Budget Endpoints ====================

@router.post("/budget", tags=["Budget"])
async def create_budget(
    user_id: str = Query(...),
    category: str = Body(...),
    allocated_amount: float = Body(...),
    period: str = Body("monthly"),
    db: Session = Depends(get_db)
):
    """Create a budget for a category"""
    try:
        budget = models.Budget(
            user_id=user_id,
            category=category,
            allocated_amount=allocated_amount,
            period=period
        )
        db.add(budget)
        db.commit()
        db.refresh(budget)
        
        return {
            "success": True,
            "budget_id": budget.id,
            "message": "Budget created successfully"
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/budget/optimize", tags=["Budget"])
async def optimize_budget(
    user_id: str = Body(...),
    target_savings_rate: float = Body(0.15),
    risk_tolerance: str = Body("medium"),
    db: Session = Depends(get_db)
):
    """Optimize budget allocation using RL agent"""
    try:
        # Get user's financial data
        transactions = db.query(models.Transaction).filter(
            models.Transaction.user_id == user_id
        ).order_by(desc(models.Transaction.date)).limit(100).all()
        
        if not transactions:
            raise HTTPException(status_code=404, detail="No transaction history found")
        
        # Calculate basic metrics
        income = sum(t.amount for t in transactions if t.type == "income")
        expenses = sum(t.amount for t in transactions if t.type == "expense")
        
        # Simple budget allocation (50/30/20 rule)
        categories = {
            "needs": income * 0.50,
            "wants": income * 0.30,
            "savings": income * 0.20,
            "emergency_fund": income * 0.10,
            "debt_payment": income * 0.10,
        }
        
        return {
            "success": True,
            "optimized_budget": categories,
            "total_allocation": sum(categories.values()),
            "projected_savings_rate": target_savings_rate,
            "message": "Budget optimized successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================== Forecast Endpoints ====================

@router.post("/forecast", tags=["Forecasting"])
async def generate_forecast(
    user_id: str = Body(...),
    forecast_days: int = Body(7),
    include_confidence: bool = Body(True),
    db: Session = Depends(get_db)
):
    """Generate income and expense forecasts"""
    try:
        # Get recent transactions
        transactions = db.query(models.Transaction).filter(
            models.Transaction.user_id == user_id,
            models.Transaction.date >= datetime.utcnow() - timedelta(days=90)
        ).all()
        
        if not transactions:
            raise HTTPException(status_code=404, detail="No transaction history found")
        
        # Calculate averages
        income_txns = [t for t in transactions if t.type == "income"]
        expense_txns = [t for t in transactions if t.type == "expense"]
        
        avg_daily_income = sum(t.amount for t in income_txns) / 90 if income_txns else 0
        avg_daily_expense = sum(t.amount for t in expense_txns) / 90 if expense_txns else 0
        
        # Generate separate income and expense forecasts
        income_forecast = []
        expense_forecast = []
        
        for i in range(forecast_days):
            date = datetime.utcnow() + timedelta(days=i+1)
            
            income_forecast.append({
                "date": date.isoformat(),
                "predicted": avg_daily_income,
                "lower": avg_daily_income * 0.8 if include_confidence else None,
                "upper": avg_daily_income * 1.2 if include_confidence else None
            })
            
            expense_forecast.append({
                "date": date.isoformat(),
                "predicted": avg_daily_expense,
                "lower": avg_daily_expense * 0.8 if include_confidence else None,
                "upper": avg_daily_expense * 1.2 if include_confidence else None
            })
        
        return {
            "success": True,
            "income_forecast": income_forecast,
            "expense_forecast": expense_forecast,
            "forecast_days": forecast_days,
            "message": "Forecast generated successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================== AI Insights ====================

@router.post("/insights", tags=["AI"])
async def generate_insights(
    user_id: str = Body(...),
    context: Optional[str] = Body(None),
    db: Session = Depends(get_db)
):
    """Generate AI-powered financial insights"""
    try:
        # Get user data
        transactions = db.query(models.Transaction).filter(
            models.Transaction.user_id == user_id
        ).order_by(desc(models.Transaction.date)).limit(50).all()
        
        if not transactions:
            raise HTTPException(status_code=404, detail="No transaction history found")
        
        # Calculate metrics
        income = sum(t.amount for t in transactions if t.type == "income")
        expenses = sum(t.amount for t in transactions if t.type == "expense")
        savings_rate = ((income - expenses) / income * 100) if income > 0 else 0
        
        # Generate insights
        insights = [
            {
                "type": "savings",
                "title": "Savings Rate Analysis",
                "description": f"Your current savings rate is {savings_rate:.1f}%. " + 
                              ("Great job! You're saving well." if savings_rate > 20 else "Consider increasing your savings."),
                "priority": "high" if savings_rate < 10 else "medium"
            }
        ]
        
        return {
            "success": True,
            "insights": insights,
            "metrics": {
                "income": income,
                "expenses": expenses,
                "savings_rate": savings_rate
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================== Anomaly Detection ====================

@router.get("/anomalies", tags=["AI"])
async def detect_anomalies(
    user_id: str = Query(...),
    db: Session = Depends(get_db)
):
    """Detect spending anomalies"""
    try:
        # Get recent transactions
        transactions = db.query(models.Transaction).filter(
            models.Transaction.user_id == user_id,
            models.Transaction.type == "expense"
        ).order_by(desc(models.Transaction.date)).limit(100).all()
        
        if not transactions:
            return {
                "success": True,
                "anomalies": [],
                "message": "No anomalies detected"
            }
        
        # Calculate average per category
        category_averages = {}
        for t in transactions:
            if t.category not in category_averages:
                category_averages[t.category] = []
            category_averages[t.category].append(t.amount)
        
        # Detect anomalies (amount > 2x average)
        anomalies = []
        for t in transactions[:20]:  # Check recent 20
            if t.category in category_averages:
                avg = sum(category_averages[t.category]) / len(category_averages[t.category])
                if t.amount > avg * 2:
                    anomalies.append({
                        "transaction_id": t.id,
                        "amount": t.amount,
                        "category": t.category,
                        "date": t.date.isoformat() if t.date else None,
                        "severity": "high" if t.amount > avg * 3 else "medium"
                    })
        
        return {
            "success": True,
            "anomalies": anomalies,
            "count": len(anomalies)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================== Agent Analysis ====================

@router.post("/agent-analysis", tags=["AI"])
async def run_agent_analysis(
    user_id: str = Body(...),
    days: int = Body(30),
    target_savings_rate: float = Body(0.30),
    risk_tolerance: str = Body("moderate"),
    db: Session = Depends(get_db)
):
    """Run comprehensive multi-agent financial analysis"""
    try:
        # Import agents
        from agents.orchestrator import FinSageOrchestrator
        
        # Get transactions
        transactions = db.query(models.Transaction).filter(
            models.Transaction.user_id == user_id,
            models.Transaction.date >= datetime.utcnow() - timedelta(days=days)
        ).all()
        
        if not transactions:
            # Return demo analysis with no data
            return {
                "success": True,
                "executive_summary": {
                    "overall_status": "No Data",
                    "health_score": 0,
                    "message": "No transaction data available for analysis"
                },
                "message": "Please add transactions to get personalized analysis"
            }
        
        # Convert to dictformat for agents
        transaction_list = [
            {
                "amount": t.amount,
                "type": t.type,
                "category": t.category,
                "description": t.description or "",
                "date": t.date.isoformat() if t.date else datetime.utcnow().isoformat()
            }
            for t in transactions
        ]
        
        # Run agent analysis
        orchestrator = FinSageOrchestrator()
        result = orchestrator.analyze(
            user_id=user_id,
            transactions=transaction_list,
            user_preferences={
                "target_savings_rate": target_savings_rate,
                "risk_tolerance": risk_tolerance
            }
        )
        
        # Store analysis result
        analysis = models.AgentAnalysis(
            user_id=user_id,
            health_score=result.get("executive_summary", {}).get("health_score"),
            risk_level=result.get("executive_summary", {}).get("risk_level"),
            executive_summary=result.get("executive_summary"),
            financial_overview=result.get("financial_overview"),
            budget_plan=result.get("budget_plan"),
            risk_assessment=result.get("risk_assessment"),
            savings_strategy=result.get("savings_strategy"),
            monitoring_alerts=result.get("monitoring_alerts")
        )
        db.add(analysis)
        db.commit()
        
        return {
            "success": True,
            **result
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Agent analysis failed: {str(e)}")
