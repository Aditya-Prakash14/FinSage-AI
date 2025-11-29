"""
Base Agent class for all FinSage AI agents
"""

from typing import Dict, Any, Optional, List
from abc import ABC, abstractmethod
import os
from dotenv import load_dotenv

load_dotenv()

try:
    from langchain_openai import ChatOpenAI
    from langchain.prompts import ChatPromptTemplate
    from langchain.schema import HumanMessage, SystemMessage
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False

try:
    import google.generativeai as genai
    GOOGLE_AI_AVAILABLE = True
except ImportError:
    GOOGLE_AI_AVAILABLE = False


class BaseAgent(ABC):
    """
    Base class for all specialized agents in FinSage AI
    
    Each agent has:
    - A specific role and expertise
    - Access to LLM for reasoning
    - Ability to process state and return decisions
    """
    
    def __init__(
        self,
        agent_name: str,
        role: str,
        model: str = "gpt-4o-mini",
        temperature: float = 0.3
    ):
        self.agent_name = agent_name
        self.role = role
        self.model = model
        self.temperature = temperature
        
        # Initialize LLM
        self.openai_key = os.getenv("OPENAI_API_KEY")
        self.google_key = os.getenv("GOOGLE_API_KEY")
        
        if LANGCHAIN_AVAILABLE and self.openai_key:
            self.llm = ChatOpenAI(
                model=model,
                temperature=temperature,
                api_key=self.openai_key
            )
            self.provider = "openai"
        elif GOOGLE_AI_AVAILABLE and self.google_key:
            genai.configure(api_key=self.google_key)
            self.gemini_model = genai.GenerativeModel('gemini-pro')
            self.llm = None
            self.provider = "google"
        else:
            self.llm = None
            self.provider = "fallback"
            print(f"⚠️ {agent_name}: No AI provider available, using rule-based logic")
    
    @abstractmethod
    def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process the current state and return agent's output
        
        Args:
            state: Current workflow state
        
        Returns:
            Updated state with agent's contributions
        """
        pass
    
    @abstractmethod
    def get_system_prompt(self) -> str:
        """Return the system prompt defining this agent's behavior"""
        pass
    
    def invoke_llm(self, prompt: str, context: Optional[Dict] = None) -> str:
        """
        Invoke the LLM with a prompt
        
        Args:
            prompt: The user prompt
            context: Optional context dictionary
        
        Returns:
            LLM response as string
        """
        system_prompt = self.get_system_prompt()
        
        if context:
            prompt = f"Context: {context}\n\n{prompt}"
        
        try:
            if self.provider == "openai" and self.llm:
                messages = [
                    SystemMessage(content=system_prompt),
                    HumanMessage(content=prompt)
                ]
                response = self.llm.invoke(messages)
                return response.content
            
            elif self.provider == "google" and self.gemini_model:
                full_prompt = f"{system_prompt}\n\n{prompt}"
                response = self.gemini_model.generate_content(full_prompt)
                return response.text
            
            else:
                return self._fallback_response(prompt)
        
        except Exception as e:
            print(f"⚠️ {self.agent_name} LLM error: {e}")
            return self._fallback_response(prompt)
    
    def _fallback_response(self, prompt: str) -> str:
        """Fallback response when LLM is unavailable"""
        return f"{self.agent_name} is processing your request (offline mode)"
    
    def extract_json(self, text: str) -> Optional[Dict]:
        """
        Extract JSON from LLM response
        
        Args:
            text: LLM response text
        
        Returns:
            Parsed JSON dict or None
        """
        import json
        import re
        
        # Try direct JSON parse
        try:
            return json.loads(text)
        except:
            pass
        
        # Try to find JSON in markdown code blocks
        json_match = re.search(r'```json\s*(.*?)\s*```', text, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except:
                pass
        
        # Try to find JSON in the text
        json_match = re.search(r'\{.*\}', text, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(0))
            except:
                pass
        
        return None
    
    def log(self, message: str, level: str = "INFO"):
        """Log agent activity"""
        print(f"[{level}] {self.agent_name}: {message}")
