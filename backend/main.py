# backend/main.py
"""
FinSage AI - Agentic AI Financial Guardian for Gig Workers
Main FastAPI application
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from datetime import datetime

from routes import finance_routes
from database.mongo_config import mongodb_manager


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle"""
    # Startup
    print("🚀 Starting FinSage AI...")
    try:
        mongodb_manager.connect()
        print("✅ Database ready")
    except Exception as e:
        print(f"⚠️  Starting without database: {e}")
    
    yield
    
    # Shutdown
    print("🛑 Shutting down FinSage AI...")
    try:
        mongodb_manager.close()
        print("✅ Database connection closed")
    except:
        pass


app = FastAPI(
    title="FinSage AI",
    description="""
    **Agentic AI Financial Guardian for Indian Gig Workers**
    
    FinSage AI combines GPT-4, Time-Series Forecasting (Prophet), and Reinforcement Learning 
    to provide intelligent financial guidance for people with unpredictable income.
    
    ## Features
    
    * 📊 **Income & Expense Forecasting** - Prophet-based predictions with confidence intervals
    * 🤖 **AI-Powered Insights** - GPT-4 generated actionable recommendations
    * 💰 **Smart Budget Optimization** - RL agent learns optimal allocations
    * 🔍 **Anomaly Detection** - Identifies unusual spending patterns
    * 🔒 **Privacy-First** - Data anonymization and encryption
    * 📈 **Real-time Analytics** - Track cash flow and savings progress
    
    ## Technology Stack
    
    - **FastAPI** - High-performance async API framework
    - **LangChain** - AI agent orchestration
    - **OpenAI GPT-4** - Natural language financial advice
    - **Prophet** - Time-series forecasting
    - **PyTorch** - Reinforcement learning for budget optimization
    - **MongoDB** - Document database for financial data
    
    """,
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://localhost:5173"],  # Frontend URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(
    finance_routes.router, 
    prefix="/api/finance", 
    tags=["Finance"]
)


@app.get("/", tags=["System"])
def root():
    """Welcome endpoint with API information"""
    return {
        "message": "Welcome to FinSage AI — Your Personal CFO",
        "tagline": "Empowering gig workers with AI-driven financial intelligence",
        "version": "1.0.0",
        "docs": "/docs",
        "features": [
            "Income/Expense Forecasting",
            "AI-Powered Budget Optimization",
            "Anomaly Detection",
            "Financial Insights & Recommendations"
        ],
        "status": "operational"
    }


@app.get("/api/status", tags=["System"])
def status():
    """API status check with database health"""
    from database.validator import quick_health_check
    
    db_health = quick_health_check()
    
    return {
        "status": "healthy" if db_health['healthy'] else "degraded",
        "database": {
            "connected": db_health['healthy'],
            "statistics": db_health.get('statistics', {})
        },
        "ai_models": "loaded",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat()
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

