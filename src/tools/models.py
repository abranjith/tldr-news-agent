from typing_extensions import TypedDict

class SearchResult(TypedDict):
    """Search result."""

    title: str
    """The title of the search result."""
    href: str
    """The URL of the search result."""
    body: str
    """The body of the search result."""