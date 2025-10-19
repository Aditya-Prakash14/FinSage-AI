# FinSage AI - Backend

Complete backend implementation for **FinSage AI**, an Agentic AI Financial Guardian for Indian gig workers.

## Features

### 🤖 AI-Powered Intelligence
- **GPT-4 Financial Advisor**: Contextual, explainable financial guidance using LangChain
- **RL Budget Optimizer**: PyTorch-based agent that learns optimal budget allocations
- **Smart Insights**: Automated analysis of spending patterns and savings opportunities

### 📊 Advanced Forecasting
- **Income Prediction**: Prophet-based time-series forecasting with confidence intervals
- **Expense Prediction**: Pattern detection with anomaly warnings
- **Volatility Analysis**: Risk scoring for income stability
- **Cash Flow Projections**: Net flow calculations with trend analysis

### 🔒 Privacy & Security
- **Data Anonymization**: PII masking and hashing
- **Audit Logging**: Compliance-ready activity tracking
- **Encryption Ready**: Framework for sensitive data encryption
- **GDPR-Compliant**: Privacy-first architecture

### 🏗️ Architecture

```
backend/
├── main.py                 # FastAPI application entry point
├── requirements.txt        # Python dependencies
├── .env.example           # Environment configuration template
│
├── routes/
│   └── finance_routes.py  # API endpoints (forecasting, budgeting, insights)
│
├── models/
│   ├── income_predictor.py    # Prophet-based income forecasting
│   ├── expense_predictor.py   # Expense prediction with anomalies
│   ├── rl_agent.py           # RL budget optimization agent
│   └── ai_advisor.py         # LangChain GPT-4 advisor
│
├── schemas/
│   ├── transaction.py     # Transaction data models
│   ├── forecast.py        # Forecast request/response schemas
│   ├── budget.py          # Budget and optimization schemas
│   └── user.py            # User and goals schemas
│
├── database/
│   ├── mongo_config.py    # MongoDB connection manager
│   └── repositories.py    # Data access layer (repository pattern)
│
└── utils/
    └── privacy.py         # Privacy, security, and audit utilities
```

## Technology Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| **API Framework** | FastAPI | High-performance async REST API |
| **AI Orchestration** | LangChain | Agent workflows and prompt engineering |
| **LLM** | OpenAI GPT-4 | Natural language financial advice |
| **Forecasting** | Prophet | Time-series income/expense prediction |
| **RL** | PyTorch | Budget optimization learning |
| **Database** | MongoDB | Document store for financial data |
| **Data Processing** | Pandas, NumPy | Analytics and transformations |

## Setup Instructions

### 1. Prerequisites

- Python 3.13+
- MongoDB (local or Atlas)
- OpenAI API key

### 2. Installation

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env and add your credentials
nano .env
```

Required environment variables:
- `OPENAI_API_KEY`: Your OpenAI API key
- `MONGODB_URI`: MongoDB connection string
- `MONGODB_DB_NAME`: Database name (default: finsage_db)

### 4. Run the Server

```bash
# Development mode with auto-reload
uvicorn main:app --reload

# Production mode
uvicorn main:app --host 0.0.0.0 --port 8000
```

Server will start at: `http://localhost:8000`
- **API Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API Endpoints

### Forecasting

#### `POST /api/finance/forecast`
Generate income/expense forecasts with AI insights

**Request:**
```json
{
  "user_id": "user123",
  "forecast_days": 7,
  "include_confidence": true
}
```

**Response:**
```json
{
  "income_forecast": [...],
  "expense_forecast": [...],
  "net_cash_flow": [...],
  "volatility_score": 0.35,
  "risk_level": "medium",
  "recommended_actions": [...]
}
```

### AI Insights

#### `POST /api/finance/insights`
Get personalized financial insights and recommendations

**Request:**
```json
{
  "user_id": "user123",
  "context": "Saving for emergency fund"
}
```

### Budget Optimization

#### `POST /api/finance/budget/optimize`
RL-powered budget optimization

**Request:**
```json
{
  "user_id": "user123",
  "target_savings_rate": 0.15,
  "risk_tolerance": "medium"
}
```

**Response:**
```json
{
  "optimized_categories": [...],
  "expected_savings": 4500,
  "confidence": 0.75,
  "reasoning": "...",
  "adjustments_made": [...]
}
```

### Transactions

#### `POST /api/finance/transactions`
Add a single transaction

#### `POST /api/finance/transactions/batch`
Bulk upload transactions

#### `GET /api/finance/transactions`
Retrieve user transactions

### Anomaly Detection

#### `GET /api/finance/anomalies?user_id=user123`
Detect unusual spending patterns with AI explanations

## Models Explained

### 1. Income Predictor (`models/income_predictor.py`)

Uses **Facebook Prophet** for time-series forecasting:
- Handles seasonality (weekly patterns for gig work)
- Confidence intervals (80%)
- Volatility scoring
- Risk level classification (low/medium/high)

### 2. Expense Predictor (`models/expense_predictor.py`)

Enhanced expense forecasting with:
- Category-wise breakdown
- Anomaly detection (>2 std devs)
- Spending pattern analysis
- Warning generation

### 3. RL Agent (`models/rl_agent.py`)

**Reinforcement Learning** budget optimizer:
- **State Features**: Income volatility, savings rate, expense pressure, etc.
- **Action Space**: Budget allocation across 8 categories
- **Policy Network**: 3-layer neural network
- **Training**: Policy gradient (simplified Q-learning)
- **Explainability**: Human-readable reasoning for recommendations

### 4. AI Advisor (`models/ai_advisor.py`)

**LangChain + GPT-4** financial advisor:
- Context-aware prompts
- Privacy-preserving (no PII in prompts)
- Structured JSON responses
- Fallback heuristics when API unavailable
- Multi-scenario support (forecast insights, budget advice, anomaly explanation)

## Database Schema

### Collections

#### `users`
```javascript
{
  _id: ObjectId,
  email: String,
  name: String,
  phone: String,
  created_at: Date,
  is_active: Boolean
}
```

#### `transactions`
```javascript
{
  _id: ObjectId,
  user_id: String,
  date: Date,
  amount: Float,
  type: "credit" | "debit",
  category: String,
  description: String,
  source: String,
  created_at: Date
}
```

#### `budgets`
```javascript
{
  _id: ObjectId,
  user_id: String,
  period: "weekly" | "monthly" | "quarterly",
  categories: [{
    category: String,
    allocated_amount: Float,
    spent_amount: Float
  }],
  total_budget: Float,
  is_active: Boolean,
  created_at: Date
}
```

## Privacy & Compliance

### Data Anonymization
- User IDs hashed with salt for analytics
- PII masked in logs and audit trails
- Email/phone partially redacted

### Audit Logging
All sensitive operations logged with:
- Timestamp
- Anonymized user ID
- Action performed
- Resource accessed

### Security Best Practices
- Input validation with Pydantic
- SQL injection prevention (NoSQL)
- CORS configuration
- Environment variable secrets
- Prepared for encryption at rest

## Development

### Running Tests
```bash
pytest tests/
```

### Code Quality
```bash
# Format code
black backend/

# Lint
pylint backend/

# Type checking
mypy backend/
```

### Adding New Features

1. **Define Schema**: Add Pydantic models in `schemas/`
2. **Create Repository**: Add data access in `database/repositories.py`
3. **Build Route**: Add endpoint in `routes/finance_routes.py`
4. **Update Docs**: Document in this README

## Deployment

### Docker
```bash
docker build -t finsage-backend .
docker run -p 8000:8000 --env-file .env finsage-backend
```

### Cloud Deployment
- **MongoDB Atlas** for managed database
- **AWS Lambda + API Gateway** for serverless
- **Railway/Render** for simple deployment
- **Kubernetes** for production scale

## Troubleshooting

### "No module named 'prophet'"
```bash
pip install prophet
```

### MongoDB Connection Issues
```bash
# Check if MongoDB is running
mongod --version

# Start MongoDB
brew services start mongodb-community  # macOS
sudo systemctl start mongod            # Linux
```

### OpenAI API Errors
- Verify API key in `.env`
- Check rate limits on OpenAI dashboard
- Ensure sufficient credits

## Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## License

MIT License - see LICENSE file for details

## Support

For issues and questions:
- GitHub Issues: [Report Bug](https://github.com/yourusername/finsage-ai/issues)
- Email: support@finsage.ai

---

**Built with ❤️ for Indian gig workers**
