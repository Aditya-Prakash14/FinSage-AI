# FinSage AI Multi-Agent System 🤖

A sophisticated **LangGraph-powered** multi-agent system for comprehensive financial analysis and guidance.

## 🎯 Overview

The FinSage AI agent system coordinates **5 specialized AI agents** that work together to provide holistic financial guidance for gig workers with irregular income.

### Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    LangGraph Orchestrator                │
│                   (Workflow Coordinator)                 │
└───────────────────┬─────────────────────────────────────┘
                    │
        ┌───────────┼───────────┐
        │           │           │
        ▼           ▼           ▼
   ┌────────┐ ┌────────┐ ┌────────┐
   │Financial│ │ Budget │ │  Risk  │
   │Analyst │ │Optimizer│ │Assessor│
   └────────┘ └────────┘ └────────┘
        │           │           │
        └───────────┼───────────┘
                    │
        ┌───────────┼───────────┐
        │           │           │
        ▼           ▼           ▼
   ┌────────┐ ┌────────┐ ┌────────┐
   │Savings │ │  Txn   │ │ Report │
   │ Coach  │ │Monitor │ │Compiler│
   └────────┘ └────────┘ └────────┘
```

## 🤖 Specialized Agents

### 1. **Financial Analyst Agent** 📊
**Role:** Analyzes transaction data and identifies patterns

**Capabilities:**
- Calculates key financial metrics (income, expenses, cash flow)
- Identifies spending patterns by category
- Detects trends and seasonal variations
- Provides data-driven insights

**Key Metrics Calculated:**
- Total Income/Expenses
- Net Cash Flow
- Savings Rate
- Income Volatility (Coefficient of Variation)
- Transaction Frequency Analysis

### 2. **Budget Optimizer Agent** 💰
**Role:** Creates optimal budget allocations using RL and AI

**Capabilities:**
- Uses Reinforcement Learning for budget optimization
- Balances essential vs discretionary spending
- Adapts to income volatility
- Maximizes savings potential

**Optimization Approach:**
- RL Agent trained on gig worker financial patterns
- 50/30/20 rule adapted for irregular income
- Dynamic allocation based on risk tolerance
- AI-enhanced recommendations

### 3. **Risk Assessor Agent** ⚠️
**Role:** Evaluates financial risks and vulnerabilities

**Capabilities:**
- Assesses income stability risk
- Evaluates cash flow vulnerabilities
- Checks emergency fund adequacy
- Prioritizes risks by severity

**Risk Categories:**
- **Income Stability Risk:** Based on volatility
- **Cash Flow Risk:** Deficit/surplus analysis
- **Savings Risk:** Adequacy of savings rate
- **Emergency Fund Risk:** Buffer capacity

**Risk Levels:** Low → Medium → High → Critical

### 4. **Savings Coach Agent** 🎯
**Role:** Guides users to build savings and achieve goals

**Capabilities:**
- Creates personalized savings strategies
- Sets progressive milestones
- Suggests micro-savings actions
- Provides motivational support

**Features:**
- Weekly savings milestones with rewards
- Fun challenges (No-Spend Weekend, Round-Up Savings)
- Behavioral psychology techniques
- Celebration-based motivation

### 5. **Transaction Monitor Agent** 🔍
**Role:** Real-time monitoring and anomaly detection

**Capabilities:**
- Detects unusual spending (>2.5 std dev)
- Identifies budget category overruns
- Flags potential duplicate transactions
- Generates severity-based alerts

**Alert Types:**
- **Anomaly:** Unusual transaction amounts
- **Budget Overrun:** Category spending limits exceeded
- **Duplicate:** Potential duplicate transactions

**Severity Levels:** Info → Warning → Urgent

## 🔄 Workflow

The **LangGraph Orchestrator** coordinates agents in a directed acyclic graph (DAG):

```
1. Financial Analyst
   ↓ (provides metrics & patterns)
2. Budget Optimizer
   ↓ (uses metrics to optimize budget)
3. Risk Assessor
   ↓ (evaluates based on metrics & budget)
4. Savings Coach
   ↓ (creates strategy based on all above)
5. Transaction Monitor
   ↓ (checks for anomalies & alerts)
6. Report Compiler
   ↓
   Comprehensive Report
```

### State Management

Agents share state through a **TypedDict**:

```python
class AgentState(TypedDict):
    user_id: str
    transactions: List[Dict]
    user_preferences: Dict
    
    financial_analysis: Dict      # From Analyst
    budget_recommendation: Dict    # From Optimizer
    risk_assessment: Dict          # From Risk Assessor
    savings_strategy: Dict         # From Savings Coach
    monitoring_alerts: Dict        # From Monitor
    
    comprehensive_report: Dict     # Final output
```

## 📊 Comprehensive Report Structure

The final report includes:

```json
{
  "user_id": "user_123",
  "timestamp": "2025-11-27T12:00:00",
  "workflow_duration": 2.34,
  
  "financial_overview": {
    "analysis": {
      "metrics": {
        "total_income": 50000,
        "total_expenses": 38000,
        "net_cash_flow": 12000,
        "savings_rate": 24.0,
        "income_volatility": 0.35
      },
      "patterns": "Top spending: Food (8000), Rent (12000)...",
      "insights": {
        "health_assessment": "Strong positive cash flow...",
        "key_findings": [...],
        "concerns": [...],
        "positives": [...]
      }
    },
    "health_score": 78.5
  },
  
  "budget_plan": {
    "budget_allocation": {
      "food_groceries": 7500,
      "rent_utilities": 15000,
      ...
    },
    "target_savings": 10000,
    "ai_recommendations": {...}
  },
  
  "risk_profile": {
    "risk_scores": {
      "income_stability_risk": {"score": 0.3, "level": "Medium"},
      ...
    },
    "ai_assessment": {
      "overall_risk_level": "Medium",
      "priority_risks": [...]
    },
    "overall_risk_score": 0.38
  },
  
  "savings_plan": {
    "strategy": {
      "encouragement": "Amazing! You're saving 24%...",
      "primary_goal": {"amount": 10000, "description": "..."},
      "micro_actions": [...],
      "psychology_tips": [...],
      "celebration_milestone": "..."
    },
    "milestones": [...],
    "challenges": [...]
  },
  
  "alerts": {
    "alerts": [
      {
        "type": "anomaly",
        "severity": "warning",
        "message": "Higher than usual expense...",
        ...
      }
    ],
    "alert_count": 3,
    "requires_action": true
  },
  
  "executive_summary": {
    "overall_status": "✅ Good",
    "health_score": 78.5,
    "key_metrics": {...},
    "top_insights": [...],
    "priority_actions": [...],
    "critical_alerts": [...],
    "savings_target": 10000,
    "risk_level": "Medium"
  }
}
```

## 🚀 Usage

### API Endpoint

```bash
POST /api/finance/agent-analysis
```

**Request Body:**
```json
{
  "user_id": "user_123",
  "days": 30,
  "target_savings_rate": 0.2,
  "risk_tolerance": "medium"
}
```

**Response:** Comprehensive report (see structure above)

### Python Usage

```python
from agents.orchestrator import get_orchestrator

orchestrator = get_orchestrator()

report = orchestrator.analyze(
    user_id="user_123",
    transactions=[...],
    user_preferences={
        "target_savings_rate": 0.2,
        "risk_tolerance": "medium"
    }
)

print(f"Health Score: {report['financial_overview']['health_score']}")
print(f"Risk Level: {report['risk_profile']['ai_assessment']['overall_risk_level']}")
```

## 🎓 Key Features

### 1. **LangGraph Orchestration**
- Directed acyclic graph (DAG) workflow
- Parallel execution where possible
- State management across agents
- Error handling and recovery

### 2. **Multi-LLM Support**
- Primary: OpenAI GPT-4
- Fallback: Google Gemini
- Graceful degradation to rule-based logic

### 3. **Financial Health Score**
- Composite score (0-100)
- Weighted components:
  - Savings Rate (30%)
  - Cash Flow (25%)
  - Risk Level (25%)
  - Transaction Tracking (20%)

### 4. **Intelligent Recommendations**
- Context-aware suggestions
- Prioritized by impact
- Actionable micro-steps
- Behavioral psychology integration

### 5. **Real-time Monitoring**
- Statistical anomaly detection
- Budget tracking
- Duplicate detection
- Severity-based alerting

## 📦 Dependencies

```bash
pip install langgraph langchain langchain-openai google-generativeai
pip install numpy pandas torch prophet
pip install fastapi pymongo
```

## 🔧 Configuration

### Environment Variables

```bash
# AI Providers
OPENAI_API_KEY=your_openai_key
GOOGLE_API_KEY=your_google_key

# MongoDB
MONGODB_URI=mongodb://...
MONGODB_DB_NAME=finsage_db
```

## 🧪 Testing

```python
# Test individual agent
from agents.financial_analyst import FinancialAnalystAgent

analyst = FinancialAnalystAgent()
state = {
    "transactions": [...],
    "user_id": "test_user"
}
result = analyst.process(state)

# Test full workflow
orchestrator = get_orchestrator()
report = orchestrator.analyze(
    user_id="test_user",
    transactions=[...],
    user_preferences={}
)
```

## 📈 Performance

- **Average Analysis Time:** 2-5 seconds
- **LLM Calls:** 5-7 per analysis (one per agent)
- **Fallback Mode:** <1 second (rule-based)
- **Concurrent Users:** Scales with FastAPI async

## 🔮 Future Enhancements

- [ ] **Goal Tracker Agent** - Track progress toward financial goals
- [ ] **Investment Advisor Agent** - Suggest investment opportunities
- [ ] **Tax Optimizer Agent** - Optimize tax planning
- [ ] **Parallel Agent Execution** - Run independent agents concurrently
- [ ] **Agent Memory** - Remember user preferences and history
- [ ] **Multi-user Benchmarking** - Compare with similar users
- [ ] **Predictive Alerts** - Predict problems before they occur

## 📝 License

Part of FinSage AI - MIT License

---

**Built with ❤️ using LangGraph, OpenAI, and financial domain expertise**
