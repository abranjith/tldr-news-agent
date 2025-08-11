"""
News Summary tools package.

This package contains all the tools for agents to consume and process news articles.
"""

from .duckduckgo import (
    duckduckgo_search_tool
)
from .google_pse import (
    google_search_tool
)

__all__ = [
    "duckduckgo_search_tool",
    "google_search_tool"
]
