# backend/models/income_predictor.py

import pandas as pd
from prophet import Prophet

def predict_income(transactions):
    """
    Input: list of transactions [{date, amount, type}]
    Output: next 7 days income forecast using Prophet
    """
    df = pd.DataFrame(transactions)

    # Filter income only
    df = df[df["type"] == "credit"]

    if df.empty:
        return {"message": "No income data found."}

    df["date"] = pd.to_datetime(df["date"])
    df.rename(columns={"date": "ds", "amount": "y"}, inplace=True)

    model = Prophet()
    model.fit(df)

    future = model.make_future_dataframe(periods=7)
    forecast = model.predict(future)

    result = forecast[["ds", "yhat"]].tail(7).to_dict(orient="records")

    return result
