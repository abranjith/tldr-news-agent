from typing import Optional

from ..config_loader import ConfigLoader
from ..llm_factory import LLMFactory

class BaseAgent:
    """Base Class for all agents."""
    
    def __init__(self, agent_name: str, config_loader: Optional[ConfigLoader] = None, 
                 llm_provider: Optional[str] = None):
        """
        Initialize the news agent.
        
        Args:
            agent_name: Name of the agent configuration to load
            config_loader: Optional config loader instance
            llm_provider: Optional LLM provider override
        """
        self.config_loader = config_loader or ConfigLoader()
        self.llm_factory = LLMFactory(self.config_loader)
        self.llm_provider = llm_provider
        
        # Load agent configuration
        self.agent_config = self.config_loader.get_agent_config(agent_name)
