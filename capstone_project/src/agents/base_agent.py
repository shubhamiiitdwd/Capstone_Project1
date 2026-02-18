"""
Base Agent Class
Foundation for all specialized agents
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List

class BaseAgent(ABC):
    """Abstract base class for all agents"""
    
    def __init__(self, name: str, role: str):
        """
        Initialize base agent
        
        Args:
            name: Agent name
            role: Agent role description
        """
        self.name = name
        self.role = role
        self.memory = []

    @property
    def llm(self):
        """Returns the currently active LLM client (Azure OpenAI).
        This is a property so it always returns the CURRENT active model."""
        from src.utils.azure_openai_client import get_active_llm_client
        return get_active_llm_client()

    @property
    def gemini(self):
        """Alias for backwards compatibility — returns the active LLM client."""
        return self.llm
        
    @abstractmethod
    def analyze(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze the given context
        
        Args:
            context: Context dictionary with relevant data
            
        Returns:
            Analysis results as dictionary
        """
        pass
    
    @abstractmethod
    def recommend(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate recommendations based on analysis
        
        Args:
            analysis: Analysis results
            
        Returns:
            List of recommendations
        """
        pass
    
    def add_to_memory(self, interaction: Dict[str, Any]):
        """Add interaction to agent memory"""
        self.memory.append(interaction)
        if len(self.memory) > 10:  # Keep last 10 interactions
            self.memory.pop(0)
    
    def get_memory_context(self) -> str:
        """Get recent memory as context string"""
        if not self.memory:
            return "No previous interactions."
        
        context = "Recent interactions:\n"
        for mem in self.memory[-3:]:
            context += f"- {mem.get('summary', 'Unknown action')}\n"
        
        return context
    
    def generate_prompt(self, context: Dict[str, Any], task: str) -> str:
        """
        Generate prompt for Gemini
        
        Args:
            context: Current context
            task: Task description
            
        Returns:
            Formatted prompt string
        """
        prompt = f"""You are {self.name}, a specialized AI agent.

Role: {self.role}

{self.get_memory_context()}

Current Context:
{self._format_context(context)}

Task: {task}

Provide your analysis and recommendations."""
        
        return prompt
    
    def _format_context(self, context: Dict[str, Any]) -> str:
        """Format context dictionary as string"""
        formatted = ""
        for key, value in context.items():
            if isinstance(value, dict):
                formatted += f"\n{key}:\n"
                for k, v in value.items():
                    formatted += f"  - {k}: {v}\n"
            else:
                formatted += f"{key}: {value}\n"
        
        return formatted
