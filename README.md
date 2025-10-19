# 🤖 FinSage AI - Your AI Financial Guardian

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![React 18](https://img.shields.io/badge/react-18.3.1-blue.svg)](https://reactjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.119.0-green.svg)](https://fastapi.tiangolo.com/)

> **The Self-Evolving Financial Guardian** — An agentic AI CFO designed specifically for Indian gig workers to manage unpredictable income using cutting-edge AI/ML technologies.

![FinSage AI Dashboard](https://img.shields.io/badge/Status-Live-success)

## 🌟 What is FinSage AI?

FinSage AI is a full-stack financial management platform that combines **GPT-4**, **Time-Series Forecasting**, and **Reinforcement Learning** to provide intelligent financial guidance for gig economy workers who face volatile income streams.

### 🎯 Key Features

- **📊 AI-Powered Forecasting** - Prophet-based income & expense predictions with 80% confidence intervals
- **🤖 GPT-4 Financial Advisor** - Natural language insights and personalized recommendations via LangChain
- **🧠 RL Budget Optimizer** - PyTorch neural network for intelligent budget allocation
- **📈 Interactive Dashboards** - Beautiful Recharts visualizations with dark mode support
- **⚡ Real-time Analysis** - Instant anomaly detection and risk assessment
- **🎨 Modern UI/UX** - React + TailwindCSS with responsive design

## 🚀 Quick Start

### Prerequisites

- Python 3.10+ 
- Node.js 18+
- OpenAI API Key (for GPT-4 insights)
- MongoDB (optional - runs in demo mode without it)

### Installation

```bash
# Clone the repository
git clone https://github.com/Aditya-Prakash14/FinSage-AI.git
cd FinSage-AI

# Backend Setup
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Add your OPENAI_API_KEY to .env

# Start backend server
uvicorn main:app --reload --port 8000

# Frontend Setup (in new terminal)
cd ../frontend
npm install
npm run dev
```

Visit **http://localhost:3000** to see the app in action! 🎉

For detailed setup instructions, see [SETUP.md](SETUP.md)

## 📸 Screenshots

### Landing Page
Clean, modern landing page with feature showcase and dark mode toggle.

### Dashboard Overview
Financial summary with income, expenses, savings rate, and volatility metrics.

### AI-Powered Forecasts
7-day predictions with confidence intervals and risk indicators.

### GPT-4 Recommendations
Personalized financial advice with actionable micro-tasks and feedback system.

## 🏗️ Architecture

```
FinSage-AI/
├── backend/              # FastAPI server
│   ├── models/          # AI/ML models
│   │   ├── rl_agent.py        # PyTorch RL agent
│   │   ├── ai_advisor.py      # GPT-4 advisor
│   │   ├── income_predictor.py   # Prophet forecasting
│   │   └── expense_predictor.py  # Expense analysis
│   ├── routes/          # API endpoints
│   ├── schemas/         # Pydantic models
│   ├── database/        # MongoDB integration
│   └── utils/           # Helper functions
│
└── frontend/            # React app
    ├── src/
    │   ├── pages/       # Landing, Dashboard
    │   ├── components/  # Reusable components
    │   ├── services/    # API client
    │   └── utils/       # Helpers
    └── public/
```

## 🛠️ Tech Stack

### Backend
- **FastAPI** - Modern async web framework
- **Prophet** - Facebook's time-series forecasting
- **OpenAI GPT-4** - Natural language insights
- **PyTorch** - Deep learning for RL agent
- **LangChain** - LLM orchestration framework
- **MongoDB** - Document database (optional)
- **Pydantic** - Data validation

### Frontend  
- **React 18** - Component-based UI
- **Vite** - Lightning-fast build tool
- **TailwindCSS** - Utility-first CSS framework
- **Recharts** - Composable charting library
- **React Router** - Client-side routing
- **Axios** - Promise-based HTTP client
- **Lucide React** - Beautiful icon set

## 📡 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/finance/forecast` | POST | Generate income/expense forecasts |
| `/api/finance/insights` | POST | Get GPT-4 financial advice |
| `/api/finance/budget/optimize` | POST | RL-powered budget optimization |
| `/api/finance/transactions/upload` | POST | Upload transaction data |
| `/api/finance/anomalies` | POST | Detect spending anomalies |
| `/api/feedback/update` | POST | Submit recommendation feedback |
| `/docs` | GET | Interactive API documentation |

## 🎨 Features in Detail

### 1. Intelligent Forecasting
- **Prophet Model** trained on transaction history
- **80% Confidence Intervals** for risk assessment
- **Multi-step predictions** (1-30 days ahead)
- **Volatility scoring** for income stability

### 2. GPT-4 Financial Advisor
- Context-aware recommendations
- Actionable micro-tasks (<7 days)
- Personalized based on spending patterns
- Warning alerts for risky behavior

### 3. Budget Optimization
- **Reinforcement Learning** agent with PyTorch
- Learns from user preferences
- Risk-adjusted recommendations
- Category-wise allocation

### 4. Beautiful Visualizations
- Income vs Expense trends
- Net cash flow projections
- Risk level indicators
- Interactive tooltips with INR formatting

### 5. Dark Mode
- Seamless theme switching
- Persistent preference storage
- Optimized for OLED displays

## 🧪 Testing

```bash
# Test with sample data
1. Open http://localhost:3000
2. Click "Get Started"
3. Click "Use Sample Data" button
4. Explore all dashboard tabs

# Upload your own CSV
Format: date, amount, type, category
Example: 2025-01-15, 5000, income, freelancing
```

## 📊 Sample Output

**Forecast Response:**
```json
{
  "income_forecast": [...],
  "expense_forecast": [...],
  "net_cash_flow": [...],
  "risk_level": "low",
  "volatility_score": 0.23,
  "confidence_score": 0.87
}
```

**AI Insights:**
```json
{
  "summary": "Your income shows high variability...",
  "action_items": [
    "Build emergency fund of ₹15,000",
    "Reduce dining expenses by 20%"
  ],
  "warnings": ["Spending exceeded income last month"],
  "confidence_score": 0.92
}
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Facebook Prophet** for time-series forecasting
- **OpenAI** for GPT-4 API
- **FastAPI** community for excellent documentation
- **TailwindCSS** for beautiful styling utilities
- **Recharts** for amazing visualization components

## 📧 Contact

**Aditya Prakash** - [@Aditya-Prakash14](https://github.com/Aditya-Prakash14)

Project Link: [https://github.com/Aditya-Prakash14/FinSage-AI](https://github.com/Aditya-Prakash14/FinSage-AI)

---

<div align="center">
  <strong>Built with ❤️ for the gig economy</strong>
  <br>
  <sub>Empowering workers with AI-driven financial intelligence</sub>
</div>
