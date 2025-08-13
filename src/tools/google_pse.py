from dataclasses import dataclass
import httpx
from pydantic import TypeAdapter
from pydantic_ai.tools import Tool


from .models import SearchResult
from .common import get_filtered_results

__all__ = ('google_search_tool',)

google_search_ta = TypeAdapter(list[SearchResult])

#Largely inspired by https://github.com/open-webui/open-webui/blob/main/backend/open_webui/retrieval/web/google_pse.py
@dataclass
class GoogleSearchTool:

    """Google search tool."""

    api_key: str
    """The API key for Google search."""

    search_engine_id: str
    """The search engine ID for Google search."""

    max_results: int | None = None
    """The maximum number of results. If None, returns results only from the first response."""

    domain_filter_list: list[str] | None = None
    """A list of domains to filter results by. If None, no filtering is applied."""

    timelimit: str | None = None
    """The time limit for the search results (e.g., 'd' for day, 'w' for week, 'm' for month, 'y' for year)."""

    async def __call__(self, query: str) -> list[SearchResult]:
        """Searches Google for the given query and returns the results.

        Args:
            query: The query to search for.

        Returns:
            The search results.
        """
        limit = self.max_results or 10
        url = "https://www.googleapis.com/customsearch/v1"
        headers = {"Content-Type": "application/json"}
        results = []
        start_index = 1  # Google PSE start parameter is 1-based
        tl = self._get_time_limit()

        while True:
            num_results_this_page = min(limit, 10)  # Google PSE max results per page is 10
            params = {
                "cx": self.search_engine_id,
                "q": query,
                "key": self.api_key,
                "num": num_results_this_page,
                "start": start_index,
            }
            if tl:
                params["dateRestrict"] = tl
            curr_results = []
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=headers, params=params)
                response.raise_for_status()
                json_response = response.json()
                curr_results = json_response.get("items", [])
            curr_len = len(curr_results)
            if curr_results:
                if self.domain_filter_list:
                    curr_results = get_filtered_results(curr_results, self.domain_filter_list)
                results.extend(curr_results)
                start_index += 10
            if curr_len < limit or (len(results) >= limit):
                break
        final_results = [
            SearchResult(
                url=result["link"],
                title=result.get("title"),
                body=result.get("snippet"),
            )
            for result in results
        ]
        return google_search_ta.validate_python(final_results)
    
    def _get_time_limit(self) -> str | None:
        """Get the time limit for the search results."""
        if self.timelimit is None:
            return None
        if self.timelimit not in ['d', 'w', 'm', 'y']:
            return None
        #for d return d1, w return w1, m return m1, y return y1
        if self.timelimit == 'd':
            self.timelimit = 'd1'
        elif self.timelimit == 'w':
            self.timelimit = 'w1'
        elif self.timelimit == 'm':
            self.timelimit = 'm1'
        elif self.timelimit == 'y':
            self.timelimit = 'y1'
        return "d1"



def google_search_tool(api_key: str, search_engine_id: str, max_results: int | None = None, domain_filter_list: list[str] | None = None, timelimit: str | None = None) -> Tool:
    """Creates a Google search tool.

    Args:
        google_client: The Google search client.
        max_results: The maximum number of results. If None, returns results only from the first response.
        domain_filter_list: A list of domains to filter results by. If None, no filtering is applied.
        timelimit: The time limit for the search results (e.g., 'd' for day, 'w' for week, 'm' for month, 'y' for year).
    """
    return Tool(
        GoogleSearchTool(api_key, search_engine_id, max_results=max_results, domain_filter_list=domain_filter_list, timelimit=timelimit).__call__,
        name='google_search',
        description='Searches Google for the given query and returns the results.',
    )