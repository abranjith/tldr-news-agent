from typing import Optional
import os 

from .base_agent import BaseAgent
from ..config_loader import ConfigLoader

class NewsAgent(BaseAgent):
    """Class for news agent."""
    
    def __init__(self, config_loader: Optional[ConfigLoader] = None, 
                 llm_provider: Optional[str] = None):
        """
        Initialize the news agent.
        
        Args:
            agent_name: Name of the agent configuration to load
            config_loader: Optional config loader instance
            llm_provider: Optional LLM provider override
        """
        super().__init__(
            agent_name="news_agent",
            config_loader=config_loader,
            llm_provider=llm_provider
        )
        
        self.search_config = self.config_loader.get_search_config()
        # Initialize the AI agent
        self._init_agent()
    
    
    def _init_agent(self) -> None:
        """Initialize the PydanticAI agent."""
        system_prompt = self.agent_config.get("system_prompt", "")
        #based on search_engine get the search tool
        se = self.search_config.get("search_engine", "duckduckgo")
        max_results = self.search_config.get("max_results", 10)
        domain_filter_list = self.search_config.get("include_domains", [])
        tools = []
        if se == "duckduckgo":
            from ..tools import duckduckgo_search_tool
            tools = [duckduckgo_search_tool(max_results=max_results, domain_filter_list=domain_filter_list)]
        elif se == "google":
            from ..tools import google_search_tool
            api_key = os.environ.get(self.search_config.get("google", {}).get("api_key_env", "GOOGLE_PSE_API_KEY"))
            search_engine_id = os.environ.get(self.search_config.get("google", {}).get("search_engine_id_env", "GOOGLE_PSE_SEARCH_ENGINE_ID"))
            tools = [google_search_tool(api_key,search_engine_id,max_results=max_results,domain_filter_list=domain_filter_list)]
        
        # Create the agent with the configured LLM (no tools needed since we handle search separately)
        self.agent = self.llm_factory.create_agent(
            system_prompt=system_prompt,
            provider=self.llm_provider,
            tools=tools
        )
    
    async def fetch_and_summarize(self, user_query : str) -> str:
        """Fetch and summarize news articles for this agent's category."""
        try:
            summary_result = await self.agent.run(user_query)
            return summary_result.output if hasattr(summary_result, 'output') else str(summary_result)

        except (ValueError, ConnectionError, TimeoutError) as e:
            return f"❌ Error fetching news in {self.agent_config.get('name', "news_agent")}: {str(e)}"
