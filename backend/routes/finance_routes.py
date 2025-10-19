from fastapi import APIRouter
from models.income_predictor import predict_income
from models.expense_predictor import predict_expense
from dotenv import load_dotenv
import os

# Load environment variables (e.g., OPENAI_API_KEY) from .env if present
load_dotenv()

try:
    # Prefer the official OpenAI SDK (installed) over deprecated langchain.llms
    from openai import OpenAI as OpenAIClient  # type: ignore
except Exception:  # SDK not available for some reason
    OpenAIClient = None  # type: ignore

router = APIRouter()

@router.post("/forecast")
def forecast(data: dict):
    """Generate short-term income/expense forecasts and 3 actionable tips.

    Expects: { "transactions": [{"date": str, "amount": float, "type": "credit"|"debit"}, ...] }
    Returns: { "income_forecast": Any, "expense_forecast": Any, "recommended_actions": str }
    """
    transactions = data.get("transactions", [])
    income = predict_income(transactions)
    expense = predict_expense(transactions)

    # Compose a concise system/user prompt
    system_prompt = (
        "You are FinSage AI, a practical financial guardian. "
        "Given the income and expense forecasts, produce exactly 3 concise micro-actions "
        "(numbered 1-3) to improve cash flow for a gig worker. Keep each under 20 words."
    )
    user_prompt = (
        f"Income Forecast: {income}\n"
        f"Expense Forecast: {expense}\n"
        "Generate 3 micro-actions."
    )

    actions_text = None
    api_key = os.getenv("OPENAI_API_KEY")

    if OpenAIClient and api_key:
        try:
            client = OpenAIClient(api_key=api_key)
            # Use Chat Completions API for broad compatibility
            completion = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.3,
                max_tokens=200,
            )
            actions_text = completion.choices[0].message.content if completion.choices else None
        except Exception:
            # Fall back to heuristic suggestions below if API call fails
            actions_text = None

    if not actions_text:
        # Heuristic fallback when no API key or SDK error
        actions_text = (
            "1) Set aside 15% of incoming payments for tax and savings.\n"
            "2) Defer non-essential purchases until weekly income exceeds forecasted expenses.\n"
            "3) Batch gigs during peak hours to raise average hourly rate."
        )

    return {
        "income_forecast": income,
        "expense_forecast": expense,
        "recommended_actions": actions_text,
    }
