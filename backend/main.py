# backend/main.py

from fastapi import FastAPI
from routes import finance_routes

app = FastAPI(
    title="FinSage AI",
    description="Agentic AI Financial Guardian for the Gig Workforce",
    version="1.0.0"
)

app.include_router(finance_routes.router, prefix="/api/finance", tags=["Finance"])

@app.get("/")
def root():
    return {"message": "Welcome to FinSage AI — your personal CFO."}
