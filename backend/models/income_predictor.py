# backend/models/income_predictor.py

import pandas as pd
from prophet import Prophet
import numpy as np
from typing import List, Dict, Optional
from datetime import datetime, timedelta


def predict_income(
    transactions: List[Dict], 
    forecast_days: int = 7,
    include_confidence: bool = True
) -> Dict:
    """
    Enhanced income prediction with confidence intervals and volatility metrics
    
    Args:
        transactions: List of transaction dicts [{date, amount, type, ...}]
        forecast_days: Number of days to forecast (1-90)
        include_confidence: Include confidence intervals
    
    Returns:
        Dictionary with forecast, volatility, and risk metrics
    """
    if not transactions:
        return {
            "forecast": [],
            "message": "No transaction data provided",
            "volatility_score": 0,
            "risk_level": "unknown"
        }
    
    df = pd.DataFrame(transactions)
    
    # Filter income only
    df = df[df["type"] == "credit"]
    
    if df.empty:
        return {
            "forecast": [],
            "message": "No income data found",
            "volatility_score": 0,
            "risk_level": "unknown"
        }
    
    # Data preparation
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date")
    
    # Aggregate daily income (sum multiple payments per day)
    daily_income = df.groupby("date")["amount"].sum().reset_index()
    daily_income.rename(columns={"date": "ds", "amount": "y"}, inplace=True)
    
    # Calculate volatility metrics
    income_values = daily_income["y"].values
    avg_income = np.mean(income_values)
    std_income = np.std(income_values)
    volatility_score = min((std_income / avg_income) if avg_income > 0 else 1.0, 1.0)
    
    # Determine risk level
    if volatility_score < 0.2:
        risk_level = "low"
    elif volatility_score < 0.5:
        risk_level = "medium"
    else:
        risk_level = "high"
    
    # Prophet model with uncertainty
    model = Prophet(
        interval_width=0.80,  # 80% confidence interval
        daily_seasonality=False,
        weekly_seasonality=True,
        yearly_seasonality=False
    )
    
    try:
        model.fit(daily_income)
    except Exception as e:
        return {
            "forecast": [],
            "message": f"Model fitting failed: {str(e)}",
            "volatility_score": volatility_score,
            "risk_level": risk_level
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
            "predicted_value": max(0, float(row["yhat"])),  # Ensure non-negative
        }
        
        if include_confidence:
            point["lower_bound"] = max(0, float(row["yhat_lower"]))
            point["upper_bound"] = max(0, float(row["yhat_upper"]))
            # Simple confidence metric (narrower interval = higher confidence)
            interval_width = row["yhat_upper"] - row["yhat_lower"]
            point["confidence"] = max(0, min(1, 1 - (interval_width / (2 * row["yhat"]))))
        
        result_forecast.append(point)
    
    return {
        "forecast": result_forecast,
        "volatility_score": float(volatility_score),
        "risk_level": risk_level,
        "avg_daily_income": float(avg_income),
        "total_historical_income": float(df["amount"].sum()),
        "income_frequency": len(daily_income),  # Number of days with income
        "message": "Forecast generated successfully"
    }
