# backend/models/ai_advisor.py
"""
LangChain-based AI Financial Advisor
Provides contextual, explainable financial guidance using GPT-4
"""

from typing import Dict, List, Optional
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

try:
    from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
    from langchain_openai import ChatOpenAI
    from langchain.chains import LLMChain
    from langchain.schema import AIMessage
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False

try:
    from openai import OpenAI as OpenAIClient
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    import google.generativeai as genai
    GOOGLE_AI_AVAILABLE = True
except ImportError:
    GOOGLE_AI_AVAILABLE = False


class FinSageAdvisor:
    """
    AI-powered financial advisor using LangChain + GPT-4
    
    Provides:
    - Personalized financial insights
    - Actionable micro-recommendations
    - Risk warnings and opportunities
    - Privacy-preserving analysis (no PII in prompts)
    """
    
    def __init__(self, model_name: str = "gpt-4o-mini", temperature: float = 0.3):
        self.model_name = model_name
        self.temperature = temperature
        self.openai_key = os.getenv("OPENAI_API_KEY")
        self.google_key = os.getenv("GOOGLE_API_KEY")
        
        # Try OpenAI first
        if LANGCHAIN_AVAILABLE and self.openai_key:
            self.llm = ChatOpenAI(
                model=model_name,
                temperature=temperature,
                api_key=self.openai_key
            )
            self.use_langchain = True
            self.ai_provider = "openai"
        elif OPENAI_AVAILABLE and self.openai_key:
            self.client = OpenAIClient(api_key=self.openai_key)
            self.use_langchain = False
            self.ai_provider = "openai"
        # Fallback to Google AI
        elif GOOGLE_AI_AVAILABLE and self.google_key:
            genai.configure(api_key=self.google_key)
            self.gemini_model = genai.GenerativeModel('gemini-pro')
            self.use_langchain = False
            self.ai_provider = "google"
            self.client = None
        else:
            self.use_langchain = False
            self.client = None
            self.ai_provider = "fallback"
            print("⚠️ No AI API keys found - using fallback mode")
    
    def generate_forecast_insights(
        self,
        income_forecast: Dict,
        expense_forecast: Dict,
        user_context: Optional[Dict] = None
    ) -> Dict[str, any]:
        """
        Generate insights from income/expense forecasts
        
        Args:
            income_forecast: Income prediction results
            expense_forecast: Expense prediction results
            user_context: Optional user preferences/goals
        
        Returns:
            Dictionary with summary, insights, action_items, warnings
        """
        # Build privacy-preserving prompt
        context_str = self._build_forecast_context(income_forecast, expense_forecast, user_context)
        
        system_prompt = """You are FinSage AI, a compassionate financial guardian for Indian gig workers.

Your role:
- Provide practical, actionable financial advice
- Focus on cash flow stability and savings
- Use simple language (avoid jargon)
- Be encouraging but honest about risks
- Suggest specific micro-actions (not generic advice)
- Consider India's economic context (UPI, informal income, etc.)

Keep responses concise and empowering."""

        user_prompt = f"""Analyze this financial forecast and provide guidance:

{context_str}

Provide:
1. A 2-sentence summary of the financial situation
2. Top 3 specific insights about income/expense patterns
3. 3 actionable micro-steps to improve cash flow (each < 20 words)
4. Any urgent warnings about shortfalls or overspending

Format as JSON with keys: summary, insights (array), action_items (array), warnings (array)"""

        if self.use_langchain and self.openai_key:
            response = self._generate_with_langchain(system_prompt, user_prompt)
        elif self.client:
            response = self._generate_with_openai(system_prompt, user_prompt)
        elif self.ai_provider == "google":
            response = self._generate_with_google(system_prompt, user_prompt)
        else:
            response = self._generate_fallback(income_forecast, expense_forecast)
        
        return response
    
    def generate_budget_advice(
        self,
        budget_allocation: Dict[str, float],
        historical_spending: Optional[Dict[str, float]] = None,
        savings_goal: Optional[float] = None
    ) -> Dict[str, any]:
        """
        Provide advice on budget allocation
        
        Args:
            budget_allocation: Recommended budget by category
            historical_spending: Past spending patterns
            savings_goal: Target savings amount
        
        Returns:
            Advice dictionary with explanations and tips
        """
        context_str = self._build_budget_context(budget_allocation, historical_spending, savings_goal)
        
        system_prompt = """You are FinSage AI, helping gig workers optimize their budgets.

Focus on:
- Comparing recommended vs actual spending
- Identifying savings opportunities
- Suggesting realistic adjustments
- Encouraging progress, not perfection

Be specific and supportive."""

        user_prompt = f"""Review this budget and provide guidance:

{context_str}

Provide:
1. Overall assessment of the budget (1 sentence)
2. 3 specific observations about allocations
3. 2-3 practical adjustments to increase savings
4. 1 encouraging message

Format as JSON with keys: assessment, observations (array), adjustments (array), encouragement"""

        if self.use_langchain and self.openai_key:
            response = self._generate_with_langchain(system_prompt, user_prompt)
        elif self.client:
            response = self._generate_with_openai(system_prompt, user_prompt)
        elif self.ai_provider == "google":
            response = self._generate_with_google(system_prompt, user_prompt)
        else:
            response = self._generate_budget_fallback(budget_allocation, historical_spending)
        
        return response
    
    def analyze_spending_anomaly(
        self,
        anomaly_data: Dict,
        recent_transactions: Optional[List[Dict]] = None
    ) -> Dict[str, any]:
        """
        Explain unusual spending patterns
        
        Args:
            anomaly_data: Details about the spending anomaly
            recent_transactions: Recent transaction list
        
        Returns:
            Explanation and recommendations
        """
        context_str = f"""Anomaly detected:
- Category: {anomaly_data.get('category', 'Unknown')}
- Amount: ₹{anomaly_data.get('amount', 0):.2f}
- Expected: ₹{anomaly_data.get('expected', 0):.2f}
- Deviation: {anomaly_data.get('deviation_pct', 0):.1f}%
- Date: {anomaly_data.get('date', 'Recent')}"""

        system_prompt = """You are FinSage AI. A spending anomaly was detected. 

Your job:
- Acknowledge the unusual spending (non-judgmentally)
- Suggest possible reasons
- Recommend corrective actions
- Remind about financial goals

Be kind but clear about the impact."""

        user_prompt = f"""{context_str}

Provide a brief, supportive response:
1. What might have caused this?
2. How does it affect their budget?
3. One specific action to get back on track

Format as JSON with keys: explanation, impact, recommended_action"""

        if self.use_langchain and self.openai_key:
            response = self._generate_with_langchain(system_prompt, user_prompt)
        elif self.client:
            response = self._generate_with_openai(system_prompt, user_prompt)
        elif self.ai_provider == "google":
            response = self._generate_with_google(system_prompt, user_prompt)
        else:
            response = {
                "explanation": "Spending exceeded expected amount for this category",
                "impact": "May reduce savings potential this period",
                "recommended_action": "Review this category and identify discretionary expenses to cut"
            }
        
        return response
    
    def _build_forecast_context(self, income_forecast, expense_forecast, user_context):
        """Build context string from forecast data"""
        inc_data = income_forecast
        exp_data = expense_forecast
        
        # Calculate aggregates
        total_predicted_income = sum(
            p.get("predicted_value", 0) 
            for p in inc_data.get("forecast", [])
        )
        total_predicted_expense = sum(
            p.get("predicted_value", 0) 
            for p in exp_data.get("forecast", [])
        )
        net_flow = total_predicted_income - total_predicted_expense
        
        context = f"""Forecast Period: Next {len(inc_data.get('forecast', []))} days

INCOME:
- Total predicted: ₹{total_predicted_income:.2f}
- Volatility: {inc_data.get('volatility_score', 0):.2f} ({inc_data.get('risk_level', 'unknown')} risk)
- Avg daily: ₹{inc_data.get('avg_daily_income', 0):.2f}

EXPENSES:
- Total predicted: ₹{total_predicted_expense:.2f}
- Pattern: {exp_data.get('spending_pattern', 'unknown')}
- Avg daily: ₹{exp_data.get('avg_daily_expense', 0):.2f}

NET CASH FLOW: ₹{net_flow:.2f}"""

        if exp_data.get('warnings'):
            context += f"\n\nWARNINGS: {', '.join(exp_data['warnings'])}"
        
        if user_context:
            context += f"\n\nUser Context: {user_context.get('note', '')}"
        
        return context
    
    def _build_budget_context(self, budget_allocation, historical_spending, savings_goal):
        """Build context for budget advice"""
        total = sum(budget_allocation.values())
        
        context = f"""Recommended Budget: ₹{total:.2f}

Allocations:"""
        
        for category, amount in sorted(budget_allocation.items(), key=lambda x: -x[1]):
            pct = (amount / total) * 100 if total > 0 else 0
            context += f"\n- {category}: ₹{amount:.2f} ({pct:.1f}%)"
            
            if historical_spending and category in historical_spending:
                hist = historical_spending[category]
                diff = amount - hist
                context += f" [vs ₹{hist:.2f} spent]"
        
        if savings_goal:
            savings_allocated = budget_allocation.get("savings", 0)
            context += f"\n\nSavings Goal: ₹{savings_goal:.2f}"
            context += f"\nAllocated: ₹{savings_allocated:.2f} ({(savings_allocated/savings_goal)*100:.1f}% of goal)"
        
        return context
    
    def _generate_with_langchain(self, system_prompt: str, user_prompt: str) -> Dict:
        """Generate response using LangChain"""
        try:
            messages = [
                SystemMessagePromptTemplate.from_template(system_prompt),
                HumanMessagePromptTemplate.from_template("{input}")
            ]
            chat_prompt = ChatPromptTemplate.from_messages(messages)
            chain = LLMChain(llm=self.llm, prompt=chat_prompt)
            
            result = chain.run(input=user_prompt)
            
            # Try to parse as JSON
            import json
            try:
                return json.loads(result)
            except:
                # If not JSON, return as summary
                return {"summary": result, "insights": [], "action_items": [], "warnings": []}
        
        except Exception as e:
            return self._error_response(str(e))
    
    def _generate_with_openai(self, system_prompt: str, user_prompt: str) -> Dict:
        """Generate response using OpenAI SDK directly"""
        try:
            completion = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=self.temperature,
                max_tokens=500
            )
            
            content = completion.choices[0].message.content
            
            # Try to parse as JSON
            import json
            try:
                return json.loads(content)
            except:
                return {"summary": content, "insights": [], "action_items": [], "warnings": []}
        
        except Exception as e:
            return self._error_response(str(e))
    
    def _generate_with_google(self, system_prompt: str, user_prompt: str) -> Dict:
        """Generate response using Google Gemini AI"""
        try:
            # Combine system and user prompts for Gemini
            full_prompt = f"{system_prompt}\n\n{user_prompt}"
            
            response = self.gemini_model.generate_content(full_prompt)
            content = response.text
            
            # Try to parse as JSON
            import json
            try:
                return json.loads(content)
            except:
                return {"summary": content, "insights": [], "action_items": [], "warnings": []}
        
        except Exception as e:
            return self._error_response(str(e))
    
    def _generate_fallback(self, income_forecast, expense_forecast) -> Dict:
        """Fallback heuristic advice when API unavailable"""
        inc_total = sum(p.get("predicted_value", 0) for p in income_forecast.get("forecast", []))
        exp_total = sum(p.get("predicted_value", 0) for p in expense_forecast.get("forecast", []))
        net_flow = inc_total - exp_total
        
        summary = f"Forecasted net cash flow: ₹{net_flow:.2f}. "
        
        if net_flow > 0:
            summary += "You're on track to save this period."
        elif net_flow < 0:
            summary += "⚠️ Expenses may exceed income."
        else:
            summary += "Breaking even - consider increasing savings."
        
        insights = []
        if income_forecast.get("risk_level") == "high":
            insights.append("Income volatility is high - build emergency fund")
        
        if expense_forecast.get("warnings"):
            insights.extend(expense_forecast["warnings"][:2])
        
        action_items = [
            "Track daily expenses to identify savings opportunities",
            f"Set aside {max(0, net_flow * 0.2):.0f} for emergency fund",
            "Review recurring subscriptions and cancel unused ones"
        ]
        
        warnings = []
        if net_flow < 0:
            warnings.append("Cash flow shortfall predicted - reduce discretionary spending")
        
        return {
            "summary": summary,
            "insights": insights[:3],
            "action_items": action_items[:3],
            "warnings": warnings,
            "confidence_score": 0.6  # Lower confidence for fallback
        }
    
    def _generate_budget_fallback(self, budget_allocation, historical_spending) -> Dict:
        """Fallback budget advice"""
        total = sum(budget_allocation.values())
        savings_pct = (budget_allocation.get("savings", 0) / total) * 100 if total > 0 else 0
        
        if savings_pct >= 15:
            assessment = f"Strong budget with {savings_pct:.1f}% savings allocation"
        else:
            assessment = f"Budget needs improvement - only {savings_pct:.1f}% to savings"
        
        return {
            "assessment": assessment,
            "observations": [
                f"Savings: ₹{budget_allocation.get('savings', 0):.2f}",
                f"Essentials: ₹{budget_allocation.get('food_groceries', 0) + budget_allocation.get('utilities', 0):.2f}",
                "Budget covers major categories"
            ],
            "adjustments": [
                "Aim for 15-20% savings rate",
                "Review entertainment and miscellaneous for cuts"
            ],
            "encouragement": "Every small step toward financial security counts!"
        }
    
    def _error_response(self, error_msg: str) -> Dict:
        """Return error response"""
        return {
            "summary": "Unable to generate AI insights at this time",
            "insights": [],
            "action_items": ["Review your transactions manually", "Check back later for AI insights"],
            "warnings": [f"Service temporarily unavailable: {error_msg}"],
            "confidence_score": 0.0
        }


# Singleton instance
_advisor_instance = None

def get_advisor() -> FinSageAdvisor:
    """Get or create advisor singleton"""
    global _advisor_instance
    if _advisor_instance is None:
        _advisor_instance = FinSageAdvisor()
    return _advisor_instance
