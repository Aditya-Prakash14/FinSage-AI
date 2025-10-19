# backend/models/expense_predictor.py

import pandas as pd
from prophet import Prophet

def predict_expense(transactions):
    """
    Input: list of transactions [{date, amount, type}]
    Output: next 7 days expense forecast using Prophet
    """
    df = pd.DataFrame(transactions)

    # Filter only expenses
    df = df[df["type"] == "debit"]

    if df.empty:
        return {"message": "No expense data found."}

    df["date"] = pd.to_datetime(df["date"])
    df.rename(columns={"date": "ds", "amount": "y"}, inplace=True)
    df["y"] = abs(df["y"])  # ensure positive expense values

    model = Prophet()
    model.fit(df)

    future = model.make_future_dataframe(periods=7)
    forecast = model.predict(future)

    result = forecast[["ds", "yhat"]].tail(7).to_dict(orient="records")

    return result
