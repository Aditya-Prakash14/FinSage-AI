"""
LangGraph-based Multi-Agent Orchestrator for FinSage AI

Coordinates multiple specialized agents in a workflow to provide
comprehensive financial guidance.
"""

from typing import Dict, Any, List, TypedDict, Annotated
import operator
from datetime import datetime

try:
    from langgraph.graph import StateGraph, END
    from langgraph.prebuilt import ToolExecutor
    LANGGRAPH_AVAILABLE = True
except ImportError:
    LANGGRAPH_AVAILABLE = False
    print("⚠️ LangGraph not available - using fallback orchestration")

from .financial_analyst import FinancialAnalystAgent
from .budget_optimizer import BudgetOptimizerAgent
from .risk_assessor import RiskAssessorAgent
from .savings_coach import SavingsCoachAgent
from .transaction_monitor import TransactionMonitorAgent


# Define the state schema for the workflow
class AgentState(TypedDict):
    """
    Shared state passed between agents in the workflow
    
    Each agent reads from and writes to this state
    """
    # Input data
    user_id: str
    transactions: List[Dict]
    user_preferences: Dict[str, Any]
    
    # Agent outputs
    financial_analysis: Dict[str, Any]
    budget_recommendation: Dict[str, Any]
    risk_assessment: Dict[str, Any]
    savings_strategy: Dict[str, Any]
    monitoring_alerts: Dict[str, Any]
    
    # Workflow metadata
    current_agent: str
    workflow_start_time: str
    errors: Annotated[List[str], operator.add]
    
    # Final output
    comprehensive_report: Dict[str, Any]


class FinSageOrchestrator:
    """
    Main orchestrator coordinating all FinSage AI agents using LangGraph
    
    Workflow:
    1. Financial Analyst - Analyzes transaction data
    2. Budget Optimizer - Creates optimal budget
    3. Risk Assessor - Evaluates financial risks
    4. Savings Coach - Provides savings strategy
    5. Transaction Monitor - Checks for alerts
    6. Compiler - Compiles final comprehensive report
    """
    
    def __init__(self):
        self.use_langgraph = LANGGRAPH_AVAILABLE
        
        # Initialize all agents
        self.financial_analyst = FinancialAnalystAgent()
        self.budget_optimizer = BudgetOptimizerAgent()
        self.risk_assessor = RiskAssessorAgent()
        self.savings_coach = SavingsCoachAgent()
        self.transaction_monitor = TransactionMonitorAgent()
        
        if self.use_langgraph:
            self.workflow = self._build_langgraph_workflow()
        else:
            self.workflow = None
    
    def _build_langgraph_workflow(self) -> StateGraph:
        """
        Build the LangGraph workflow
        
        Creates a directed acyclic graph (DAG) where agents process
        state sequentially and in parallel where possible.
        """
        # Create workflow graph
        workflow = StateGraph(AgentState)
        
        # Add nodes (agents)
        workflow.add_node("analyst", self._analyst_node)
        workflow.add_node("optimizer", self._optimizer_node)
        workflow.add_node("risk_assessor", self._risk_assessor_node)
        workflow.add_node("savings_coach", self._savings_coach_node)
        workflow.add_node("monitor", self._monitor_node)
        workflow.add_node("compiler", self._compiler_node)
        
        # Define edges (workflow)
        workflow.set_entry_point("analyst")
        
        # Sequential flow
        workflow.add_edge("analyst", "optimizer")
        workflow.add_edge("optimizer", "risk_assessor")
        workflow.add_edge("risk_assessor", "savings_coach")
        workflow.add_edge("savings_coach", "monitor")
        workflow.add_edge("monitor", "compiler")
        
        # End after compilation
        workflow.add_edge("compiler", END)
        
        return workflow.compile()
    
    def _analyst_node(self, state: AgentState) -> AgentState:
        """Financial Analyst agent node"""
        state["current_agent"] = "Financial Analyst"
        try:
            return self.financial_analyst.process(state)
        except Exception as e:
            state["errors"] = state.get("errors", []) + [f"Analyst error: {str(e)}"]
            return state
    
    def _optimizer_node(self, state: AgentState) -> AgentState:
        """Budget Optimizer agent node"""
        state["current_agent"] = "Budget Optimizer"
        try:
            return self.budget_optimizer.process(state)
        except Exception as e:
            state["errors"] = state.get("errors", []) + [f"Optimizer error: {str(e)}"]
            return state
    
    def _risk_assessor_node(self, state: AgentState) -> AgentState:
        """Risk Assessor agent node"""
        state["current_agent"] = "Risk Assessor"
        try:
            return self.risk_assessor.process(state)
        except Exception as e:
            state["errors"] = state.get("errors", []) + [f"Risk Assessor error: {str(e)}"]
            return state
    
    def _savings_coach_node(self, state: AgentState) -> AgentState:
        """Savings Coach agent node"""
        state["current_agent"] = "Savings Coach"
        try:
            return self.savings_coach.process(state)
        except Exception as e:
            state["errors"] = state.get("errors", []) + [f"Savings Coach error: {str(e)}"]
            return state
    
    def _monitor_node(self, state: AgentState) -> AgentState:
        """Transaction Monitor agent node"""
        state["current_agent"] = "Transaction Monitor"
        try:
            return self.transaction_monitor.process(state)
        except Exception as e:
            state["errors"] = state.get("errors", []) + [f"Monitor error: {str(e)}"]
            return state
    
    def _compiler_node(self, state: AgentState) -> AgentState:
        """Compile comprehensive report from all agent outputs"""
        state["current_agent"] = "Report Compiler"
        
        try:
            report = {
                "user_id": state.get("user_id"),
                "timestamp": datetime.utcnow().isoformat(),
                "workflow_duration": self._calculate_duration(state.get("workflow_start_time")),
                
                # Financial Overview
                "financial_overview": {
                    "analysis": state.get("financial_analysis", {}),
                    "health_score": self._calculate_health_score(state),
                },
                
                # Budget Plan
                "budget_plan": state.get("budget_recommendation", {}),
                
                # Risk Profile
                "risk_profile": state.get("risk_assessment", {}),
                
                # Savings Plan
                "savings_plan": state.get("savings_strategy", {}),
                
                # Alerts & Monitoring
                "alerts": state.get("monitoring_alerts", {}),
                
                # Executive Summary
                "executive_summary": self._create_executive_summary(state),
                
                # Errors (if any)
                "errors": state.get("errors", []),
            }
            
            state["comprehensive_report"] = report
            
        except Exception as e:
            state["errors"] = state.get("errors", []) + [f"Compiler error: {str(e)}"]
            state["comprehensive_report"] = {"error": str(e)}
        
        return state
    
    def analyze(
        self,
        user_id: str,
        transactions: List[Dict],
        user_preferences: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Run the complete multi-agent analysis
        
        Args:
            user_id: User identifier
            transactions: List of transaction dictionaries
            user_preferences: Optional user preferences (target_savings_rate, risk_tolerance, etc.)
        
        Returns:
            Comprehensive financial report from all agents
        """
        print(f"🚀 Starting FinSage AI Multi-Agent Analysis for user {user_id}")
        print(f"   Analyzing {len(transactions)} transactions")
        
        # Initialize state
        initial_state = AgentState(
            user_id=user_id,
            transactions=transactions,
            user_preferences=user_preferences or {},
            financial_analysis={},
            budget_recommendation={},
            risk_assessment={},
            savings_strategy={},
            monitoring_alerts={},
            current_agent="",
            workflow_start_time=datetime.utcnow().isoformat(),
            errors=[],
            comprehensive_report={}
        )
        
        if self.use_langgraph and self.workflow:
            # Use LangGraph workflow
            final_state = self.workflow.invoke(initial_state)
        else:
            # Fallback: sequential execution
            final_state = self._fallback_execution(initial_state)
        
        report = final_state.get("comprehensive_report", {})
        
        print(f"✅ Analysis complete. Report generated with {len(report)} sections")
        
        return report
    
    def _fallback_execution(self, state: AgentState) -> AgentState:
        """Fallback execution when LangGraph is not available"""
        print("⚠️ Using fallback sequential execution")
        
        # Execute agents in sequence
        agents = [
            ("Financial Analyst", self.financial_analyst),
            ("Budget Optimizer", self.budget_optimizer),
            ("Risk Assessor", self.risk_assessor),
            ("Savings Coach", self.savings_coach),
            ("Transaction Monitor", self.transaction_monitor),
        ]
        
        for agent_name, agent in agents:
            try:
                print(f"   → {agent_name}...")
                state["current_agent"] = agent_name
                state = agent.process(state)
            except Exception as e:
                error_msg = f"{agent_name} error: {str(e)}"
                state["errors"] = state.get("errors", []) + [error_msg]
                print(f"   ⚠️ {error_msg}")
        
        # Compile report
        state = self._compiler_node(state)
        
        return state
    
    def _calculate_health_score(self, state: AgentState) -> float:
        """
        Calculate overall financial health score (0-100)
        
        Based on:
        - Savings rate
        - Income stability
        - Cash flow
        - Risk level
        """
        analysis = state.get("financial_analysis", {})
        metrics = analysis.get("metrics", {})
        risks = state.get("risk_assessment", {})
        
        # Savings rate component (0-30 points)
        savings_rate = metrics.get("savings_rate", 0)
        savings_score = min(savings_rate * 1.5, 30)
        
        # Cash flow component (0-25 points)
        net_cash_flow = metrics.get("net_cash_flow", 0)
        total_income = metrics.get("total_income", 1)
        cash_flow_ratio = net_cash_flow / total_income if total_income > 0 else 0
        cash_flow_score = min(max(cash_flow_ratio * 100, 0), 25)
        
        # Risk component (0-25 points) - inverse of risk
        overall_risk = risks.get("overall_risk_score", 0.5)
        risk_score = (1 - overall_risk) * 25
        
        # Transaction tracking component (0-20 points)
        txn_count = metrics.get("transaction_count", 0)
        tracking_score = min(txn_count / 30 * 20, 20)
        
        total_score = savings_score + cash_flow_score + risk_score + tracking_score
        
        return round(total_score, 1)
    
    def _create_executive_summary(self, state: AgentState) -> Dict[str, Any]:
        """Create executive summary of all agent findings"""
        analysis = state.get("financial_analysis", {})
        budget = state.get("budget_recommendation", {})
        risks = state.get("risk_assessment", {})
        savings = state.get("savings_strategy", {})
        alerts = state.get("monitoring_alerts", {})
        
        # Extract key points
        metrics = analysis.get("metrics", {})
        insights = analysis.get("insights", {})
        
        health_score = self._calculate_health_score(state)
        
        # Determine overall status
        if health_score >= 75:
            status = "Excellent"
            emoji = "🌟"
        elif health_score >= 60:
            status = "Good"
            emoji = "✅"
        elif health_score >= 40:
            status = "Fair"
            emoji = "⚠️"
        else:
            status = "Needs Attention"
            emoji = "🚨"
        
        summary = {
            "overall_status": f"{emoji} {status}",
            "health_score": health_score,
            "key_metrics": {
                "monthly_income": metrics.get("total_income", 0),
                "monthly_expenses": metrics.get("total_expenses", 0),
                "savings_rate": metrics.get("savings_rate", 0),
                "net_cash_flow": metrics.get("net_cash_flow", 0)
            },
            "top_insights": insights.get("key_findings", [])[:3],
            "priority_actions": self._get_priority_actions(state),
            "critical_alerts": [
                a for a in alerts.get("alerts", [])
                if a.get("severity") in ["urgent", "warning"]
            ][:3],
            "savings_target": budget.get("target_savings", 0),
            "risk_level": risks.get("ai_assessment", {}).get("overall_risk_level", "Unknown")
        }
        
        return summary
    
    def _get_priority_actions(self, state: AgentState) -> List[str]:
        """Extract top priority actions across all agents"""
        actions = []
        
        # From savings strategy
        savings = state.get("savings_strategy", {})
        strategy = savings.get("strategy", {})
        micro_actions = strategy.get("micro_actions", [])
        if micro_actions:
            actions.extend(micro_actions[:2])
        
        # From risk assessment
        risks = state.get("risk_assessment", {})
        ai_assessment = risks.get("ai_assessment", {})
        priority_risks = ai_assessment.get("priority_risks", [])
        for risk in priority_risks[:1]:
            if risk.get("timeline") == "immediate":
                actions.append(risk.get("mitigation", ""))
        
        # From budget recommendations
        budget = state.get("budget_recommendation", {})
        ai_recs = budget.get("ai_recommendations", {})
        adjustments = ai_recs.get("adjustments", [])
        if adjustments:
            actions.append(adjustments[0])
        
        return actions[:5]  # Top 5 actions
    
    def _calculate_duration(self, start_time: str) -> float:
        """Calculate workflow duration in seconds"""
        try:
            start = datetime.fromisoformat(start_time)
            duration = (datetime.utcnow() - start).total_seconds()
            return round(duration, 2)
        except:
            return 0.0


# Singleton instance
_orchestrator_instance = None

def get_orchestrator() -> FinSageOrchestrator:
    """Get or create orchestrator singleton"""
    global _orchestrator_instance
    if _orchestrator_instance is None:
        _orchestrator_instance = FinSageOrchestrator()
    return _orchestrator_instance
