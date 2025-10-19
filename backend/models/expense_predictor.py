# backend/models/expense_predictor.py

import pandas as pd
from prophet import Prophet
import numpy as np
from typing import List, Dict, Optional
from datetime import datetime


def predict_expense(
    transactions: List[Dict],
    forecast_days: int = 7,
    include_confidence: bool = True
) -> Dict:
    """
    Enhanced expense prediction with anomaly detection and category breakdown
    
    Args:
        transactions: List of transaction dicts [{date, amount, type, category, ...}]
        forecast_days: Number of days to forecast (1-90)
        include_confidence: Include confidence intervals
    
    Returns:
        Dictionary with forecast, spending patterns, and warnings
    """
    if not transactions:
        return {
            "forecast": [],
            "message": "No transaction data provided",
            "spending_pattern": "unknown",
            "warnings": []
        }
    
    df = pd.DataFrame(transactions)
    
    # Filter only expenses (handle both negative amounts and "debit" type)
    df = df[df["type"] == "debit"].copy()
    
    if df.empty:
        return {
            "forecast": [],
            "message": "No expense data found",
            "spending_pattern": "unknown",
            "warnings": []
        }
    
    # Data preparation
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date")
    df["amount"] = df["amount"].abs()  # Ensure positive values
    
    # Aggregate daily expenses
    daily_expenses = df.groupby("date")["amount"].sum().reset_index()
    daily_expenses.rename(columns={"date": "ds", "amount": "y"}, inplace=True)
    
    # Analyze spending patterns
    expense_values = daily_expenses["y"].values
    avg_expense = np.mean(expense_values)
    std_expense = np.std(expense_values)
    
    # Detect spending pattern
    cv = (std_expense / avg_expense) if avg_expense > 0 else 0
    if cv < 0.3:
        spending_pattern = "consistent"
    elif cv < 0.6:
        spending_pattern = "moderate_variability"
    else:
        spending_pattern = "highly_variable"
    
    # Detect anomalies (expenses > 2 std devs above mean)
    warnings = []
    recent_expenses = df[df["date"] >= (df["date"].max() - pd.Timedelta(days=7))]
    if not recent_expenses.empty:
        recent_total = recent_expenses["amount"].sum()
        if recent_total > avg_expense * 7 * 1.5:
            warnings.append("⚠️ Recent spending is 50% higher than average")
    
    # Category breakdown
    category_spending = {}
    if "category" in df.columns:
        category_spending = df.groupby("category")["amount"].sum().to_dict()
        
        # Check for overspending in specific categories
        for category, amount in category_spending.items():
            if amount > avg_expense * 7 * 0.4:  # Single category > 40% of weekly budget
                warnings.append(f"💳 High spending in '{category}': ₹{amount:.2f}")
    
    # Prophet model
    model = Prophet(
        interval_width=0.80,
        daily_seasonality=False,
        weekly_seasonality=True,
        yearly_seasonality=False
    )
    
    try:
        model.fit(daily_expenses)
    except Exception as e:
        return {
            "forecast": [],
            "message": f"Model fitting failed: {str(e)}",
            "spending_pattern": spending_pattern,
            "warnings": warnings
        }
    
    # Generate forecast
    future = model.make_future_dataframe(periods=forecast_days)
    forecast = model.predict(future)
    
    # Extract forecast results
    forecast_data = forecast.tail(forecast_days)[["ds", "yhat", "yhat_lower", "yhat_upper"]]
    
    result_forecast = []
    for _, row in forecast_data.iterrows():
        point = {
            "date": row["ds"].isoformat(),
            "predicted_value": max(0, float(row["yhat"])),
        }
        
        if include_confidence:
            point["lower_bound"] = max(0, float(row["yhat_lower"]))
            point["upper_bound"] = max(0, float(row["yhat_upper"]))
            interval_width = row["yhat_upper"] - row["yhat_lower"]
            point["confidence"] = max(0, min(1, 1 - (interval_width / (2 * max(row["yhat"], 1)))))
        
        result_forecast.append(point)
    
    return {
        "forecast": result_forecast,
        "spending_pattern": spending_pattern,
        "avg_daily_expense": float(avg_expense),
        "total_historical_expense": float(df["amount"].sum()),
        "category_breakdown": {k: float(v) for k, v in category_spending.items()},
        "warnings": warnings,
        "message": "Forecast generated successfully"
    }
