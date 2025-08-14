from typing import Optional, List

from .base_agent import BaseAgent
from ..config_loader import ConfigLoader

class FormattingAgent(BaseAgent):
    """Class for formatting agent."""
    
    def __init__(self, config_loader: Optional[ConfigLoader] = None, 
                 llm_provider: Optional[str] = None, 
                 user_interests: Optional[List[str]] = None):
        """
        Initialize the formatting agent.
        
        Args:
            agent_name: Name of the agent configuration to load
            config_loader: Optional config loader instance
            llm_provider: Optional LLM provider override
            user_interests: Optional list of user interests to customize formatting
        """
        super().__init__(
            agent_name="formatting_agent",
            config_loader=config_loader,
            llm_provider=llm_provider
        )
        
        # Initialize the AI agent
        self._init_agent(user_interests)

    def _init_agent(self, user_interests: Optional[List[str]]) -> None:
        """Initialize the PydanticAI agent."""
        system_prompt = self.agent_config.get("system_prompt", "")
        user_interests_str = ""
        if user_interests:
            interests = ", ".join(user_interests)
            user_interests_str = f"User is specifically interested in these subjects: {interests}. So order the topics by these subjects, ensuring that the most important or impactful topics are prioritized."
        if "{{user_interests}}" in system_prompt:
            system_prompt = system_prompt.replace("{{user_interests}}", user_interests_str)

        # Create the agent with the configured LLM (no tools needed since we handle search separately)
        self.agent = self.llm_factory.create_agent(
            system_prompt=system_prompt,
            provider=self.llm_provider
        )

    async def format(self, news_stories: List[str]) -> str:
        """Format news articles for this agent's category."""
        try:
            if not news_stories:
                return "No news stories to format."
            # string.join new line and dashes
            dashes = "-" * 40
            stories = f"\n\n{dashes}\n\n".join(news_stories)
            formatted_stories = await self.agent.run(stories)
            return formatted_stories.output if hasattr(formatted_stories, 'output') else str(formatted_stories)

        except (ValueError, ConnectionError, TimeoutError) as e:
            return f"❌ Error formatting in {self.agent_config.get('name', "formatting_agent")}: {str(e)}"
