# FinSage AI - Setup & Run Guide

## 🚀 Quick Start

### Prerequisites
- **Python 3.10+** (for backend)
- **Node.js 18+** (for frontend)
- **MongoDB** (optional - app runs in demo mode without it)
- **OpenAI API Key** (for GPT-4 insights)

---

## 📦 Backend Setup

### 1. Navigate to backend directory
```bash
cd backend
```

### 2. Create virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On macOS/Linux
# venv\Scripts\activate   # On Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment variables
```bash
cp .env.example .env
```

Edit `.env` and add your OpenAI API key:
```env
OPENAI_API_KEY=sk-your-openai-api-key-here
MONGODB_URI=mongodb://localhost:27017  # Optional
DATABASE_NAME=finsage
```

### 5. Start the backend server
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Backend will be available at: **http://localhost:8000**  
API Documentation: **http://localhost:8000/docs**

---

## 🎨 Frontend Setup

### 1. Navigate to frontend directory
```bash
cd frontend
```

### 2. Install dependencies
```bash
npm install
```

### 3. Start the development server
```bash
npm run dev
```

Frontend will be available at: **http://localhost:3000**

---

## 🧪 Testing the Application

### Step 1: Access the Landing Page
Open **http://localhost:3000** in your browser

### Step 2: Navigate to Dashboard
Click "Get Started" button

### Step 3: Generate Sample Data
On the Dashboard Overview tab, click "Use Sample Data"

This will:
- Generate 60 days of realistic transaction data
- Upload to the backend
- Generate 7-day forecast
- Get AI-powered insights from GPT-4

### Step 4: Explore Features

**Overview Tab:**
- View financial summary (income, expenses, savings)
- See savings rate and volatility metrics
- Monitor risk level

**Forecast Tab:**
- Income prediction chart with confidence intervals
- Expense prediction chart
- Net cash flow visualization
- Risk indicators

**Insights Tab:**
- GPT-4 generated financial recommendations
- Actionable micro-tasks
- Warning alerts
- Like/dislike feedback system

---

## 🔧 Development Mode (No MongoDB)

The app automatically runs in **demo mode** if MongoDB is unavailable:

```bash
# Backend will show:
⚠️ Warning: MongoDB not available. Using in-memory storage.
API will run in demo mode without persistence.
```

All features work except data persistence across server restarts.

---

## 📊 API Endpoints

### Generate Forecast
```bash
POST /api/finance/forecast
{
  "user_id": "demo_user_001",
  "days": 7,
  "include_confidence": true
}
```

### Get AI Insights
```bash
POST /api/finance/insights
{
  "user_id": "demo_user_001",
  "user_query": "Help me manage my finances"
}
```

### Upload Transactions
```bash
POST /api/finance/transactions/upload
{
  "user_id": "demo_user_001",
  "transactions": [...]
}
```

### Optimize Budget
```bash
POST /api/finance/budget/optimize
{
  "user_id": "demo_user_001",
  "income": 50000,
  "expenses": {...}
}
```

---

## 🎯 Features

### ✅ Completed
- ✅ Full FastAPI backend with async endpoints
- ✅ Prophet-based time-series forecasting
- ✅ GPT-4 AI advisor with LangChain
- ✅ PyTorch RL agent for budget optimization
- ✅ React + TailwindCSS frontend
- ✅ Recharts visualizations
- ✅ Dark mode support
- ✅ Responsive design
- ✅ Sample data generation
- ✅ CSV file upload
- ✅ Real-time API integration

### 🔄 In Progress
- MongoDB integration testing
- User authentication
- Advanced analytics tab

---

## 🐛 Troubleshooting

### Backend Issues

**Problem:** `ModuleNotFoundError`  
**Solution:** Ensure virtual environment is activated and all dependencies installed:
```bash
source venv/bin/activate
pip install -r requirements.txt
```

**Problem:** MongoDB connection error  
**Solution:** MongoDB is optional. App runs in demo mode without it.

**Problem:** OpenAI API errors  
**Solution:** Check your API key in `.env` file and ensure you have credits

### Frontend Issues

**Problem:** `npm install` fails  
**Solution:** Delete `node_modules` and `package-lock.json`, then reinstall:
```bash
rm -rf node_modules package-lock.json
npm install
```

**Problem:** Vite port already in use  
**Solution:** Change port in `vite.config.js` or kill process on port 3000:
```bash
lsof -ti:3000 | xargs kill -9
```

**Problem:** API calls fail (CORS)  
**Solution:** Ensure backend is running on port 8000 and Vite proxy is configured

---

## 📝 Tech Stack

### Backend
- **FastAPI** - Modern async web framework
- **Prophet** - Time-series forecasting
- **OpenAI GPT-4** - Natural language insights
- **PyTorch** - Reinforcement learning
- **LangChain** - LLM orchestration
- **MongoDB** - Document database (optional)

### Frontend
- **React 18** - UI library
- **Vite** - Build tool
- **TailwindCSS** - Utility-first CSS
- **Recharts** - Chart library
- **React Router** - Routing
- **Axios** - HTTP client

---

## 🎨 Component Structure

```
frontend/src/
├── pages/
│   ├── LandingPage.jsx       # Hero page with features
│   └── Dashboard.jsx          # Main app dashboard
├── components/
│   ├── TransactionUpload.jsx  # CSV upload + sample data
│   ├── ForecastCharts.jsx     # Recharts visualizations
│   ├── AIRecommendations.jsx  # GPT-4 insights display
│   └── FinancialSummary.jsx   # Stats cards
├── services/
│   └── api.js                 # Axios API client
└── utils/
    └── helpers.js             # Utility functions
```

---

## 📚 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Prophet Forecasting](https://facebook.github.io/prophet/)
- [OpenAI API](https://platform.openai.com/docs)
- [TailwindCSS](https://tailwindcss.com/)
- [Recharts](https://recharts.org/)

---

## 🤝 Support

For issues or questions:
1. Check the troubleshooting section above
2. Review backend logs in terminal
3. Check browser console for frontend errors
4. Verify API endpoints at http://localhost:8000/docs

---

## 📄 License

See LICENSE file for details.
