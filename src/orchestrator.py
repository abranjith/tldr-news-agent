"""Main orchestrator for coordinating news agents and generating reports."""

import asyncio
from datetime import datetime
from pathlib import Path
from typing import Optional

from .agents import NewsAgent, FormattingAgent
from .config_loader import ConfigLoader
from .llm_factory import LLMFactory


class NewsOrchestrator:
    """Orchestrates multiple news agents to create comprehensive reports."""
    
    def __init__(self, config_loader: Optional[ConfigLoader] = None, 
                 llm_provider: Optional[str] = None):
        """
        Initialize the news orchestrator.
        
        Args:
            config_loader: Optional config loader instance
            llm_provider: Optional LLM provider override
        """
        self.config_loader = config_loader or ConfigLoader()
        self.llm_provider = llm_provider
        self.llm_factory = LLMFactory(self.config_loader)
        
        # Load configurations
        self.orchestrator_config = self.config_loader.get_orchestrator_config()
        self.output_config = self.config_loader.get_output_config()
        user_interests = self.orchestrator_config.get("user_interests", [])
        
        # Initialize agents
        self.news_agent = NewsAgent(
            config_loader=self.config_loader,
            llm_provider=self.llm_provider
        )
        self.formatting_agent = FormattingAgent(
            config_loader=self.config_loader,
            llm_provider=self.llm_provider,
            user_interests=user_interests
        )

    async def generate_news_report(self, *topics, save_to_file: Optional[bool] = True, output_path: Optional[str] = None) -> str:
        """
        Generate a comprehensive news report.
        
        Args:
            topics: list of topics to filter news articles
            output_path: Optional path to save the report file
            
        Returns:
            The generated report content (markdown format)
        """
        if not topics:
            topics = self.orchestrator_config.get("default_topics", [])
        
        # Gather summaries from all agents (sequentially to avoid overwhelming the search API)
        summaries = []
        
        for topic in topics:
            try:
                resp = await self.news_agent.fetch_and_summarize(topic)
                if resp:
                    summaries.append(resp)

                # Small delay to be respectful to the search API
                await asyncio.sleep(2)
                
            except Exception as e:
                error_msg = f"❌ Failed to fetch {topic}: {str(e)}"
                print(error_msg)
        
        # Generate the final report
        if not summaries:
            return "⚠️ No news summaries available for the specified topics."
        # Format the summaries using the formatting agent
        formatted_report = await self.formatting_agent.format(summaries)
        final_report = await self._create_final_report(formatted_report)

        if not save_to_file:
            return final_report

        # Save the report
        if output_path is None:
            output_path = self._get_default_output_path()

        await self._save_report(final_report, output_path)
        return final_report
    
    async def _create_final_report(self, news_report: str) -> str:
        """
        Create the final structured report.
        
        Args:
            news_report: Formatted news report content (markdown format)
            
        Returns:
            Formatted report content
        """
        current_time = datetime.now()
        date_str = current_time.strftime("%B %d, %Y")
        time_str = current_time.strftime("%I:%M %p")
        
        # news_report has markdown content, so we can directly format it with key as header and nicely format date in human friendly way
        report_content = f"**Date:** {date_str}  \n"
        report_content += f"**Time:** {time_str}  \n"
        report_content += f"{news_report}\n"

        return report_content

    def _get_default_output_path(self) -> str:
        """Get the default output file path."""
        current_date = datetime.now()
        dir_path = self.output_config.get("directory", "./reports")
        date_format = self.output_config.get("date_format", "%Y-%m-%d-%H-%M")
        filename_pattern = self.output_config.get("filename_pattern", "news_{date}.md")
        
        date_str = current_date.strftime(date_format)
        filename = filename_pattern.format(date=date_str)
        
        # Ensure the directory exists
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        return str(Path(dir_path) / filename)
    
    async def _save_report(self, content: str, output_path: str) -> None:
        """
        Save the report to a file.
        
        Args:
            content: Report content to save
            output_path: Path to save the file
        """
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(content)
        except IOError as e:
            raise IOError(f"Failed to save report to {output_path}: {str(e)}") from e
    
async def main():
    """Main function for running the news orchestrator."""
    orchestrator = NewsOrchestrator()
    await orchestrator.generate_news_report()


if __name__ == "__main__":
    asyncio.run(main())
