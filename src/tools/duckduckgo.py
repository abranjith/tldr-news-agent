import functools
from dataclasses import dataclass
import anyio
import anyio.to_thread
from pydantic import TypeAdapter
from pydantic_ai.tools import Tool

from .models import SearchResult
from .common import get_filtered_results

try:
    from ddgs import DDGS
except ImportError as _import_error:
    raise ImportError(
        'Please install `ddgs` to use the DuckDuckGo search tool, '
        'you can use the `duckduckgo` optional group — `pip install "pydantic-ai-slim[duckduckgo]"`'
    ) from _import_error

__all__ = ('duckduckgo_search_tool',)

duckduckgo_ta = TypeAdapter(list[SearchResult])

#copy of https://github.com/pydantic/pydantic-ai/blob/main/pydantic_ai_slim/pydantic_ai/common_tools/duckduckgo.py with filtering support
@dataclass
class DuckDuckGoSearchTool:
    """The DuckDuckGo search tool."""

    client: DDGS
    """The DuckDuckGo search client."""

    max_results: int | None = None
    """The maximum number of results. If None, returns results only from the first response."""

    domain_filter_list: list[str] | None = None
    """A list of domains to filter results by. If None, no filtering is applied."""

    timelimit: str | None = None
    """The time limit for the search results (e.g., 'd' for day, 'w' for week, 'm' for month, 'y' for year)."""

    async def __call__(self, query: str) -> list[SearchResult]:
        """Searches DuckDuckGo for the given query and returns the results.

        Args:
            query: The query to search for.

        Returns:
            The search results.
        """
        limit = self.max_results or 10
        results = []
        #since we are using the news endpoint, there is no need to stress "news" in the query
        query = query.replace(" news ", " ").strip()
        # if ends with " news", remove it
        if query.endswith(" news"):
            query = query[:-5].strip()

        while True:
            search = functools.partial(self.client.news, max_results=limit, timelimit=self.timelimit)
            curr_results = await anyio.to_thread.run_sync(search, query)
            if not curr_results:
                break
            curr_len = len(curr_results)
            if self.domain_filter_list:
                curr_results = get_filtered_results(curr_results, self.domain_filter_list)
            results.extend(curr_results)
            if curr_len < limit or (len(results) >= limit):
                break
        final_results = [
            SearchResult(
                url=result["url"],
                title=result.get("title"),
                body=result.get("body"),
            )
            for result in results
        ]
        return duckduckgo_ta.validate_python(final_results)



def duckduckgo_search_tool(duckduckgo_client: DDGS | None = None, max_results: int | None = None, domain_filter_list: list[str] | None = None, timelimit: str | None = None) -> Tool:
    """Creates a DuckDuckGo search tool.

    Args:
        duckduckgo_client: The DuckDuckGo search client.
        max_results: The maximum number of results. If None, returns results only from the first response.
        domain_filter_list: A list of domains to filter results by. If None, no filtering is applied.
        timelimit: The time limit for the search results (e.g., 'd' for day, 'w' for week, 'm' for month, 'y' for year).
    """
    return Tool(
        DuckDuckGoSearchTool(client=duckduckgo_client or DDGS(), max_results=max_results, domain_filter_list=domain_filter_list, timelimit=timelimit).__call__,
        name='duckduckgo_search',
        description='Searches DuckDuckGo for the given query and returns the results.',
    )