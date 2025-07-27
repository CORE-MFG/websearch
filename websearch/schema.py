# Standard Library
from typing import List
# Third Party
from pydantic import BaseModel, HttpUrl


class SearchResult(BaseModel):
    """
    A search result from a web search.

    Args:
        url: The URL of the search result
        title: The title of the search result
        snippet: The snippet of the search result
        content: The content of the search result
    """
    url: HttpUrl
    title: str
    snippet: str
    content: str

class SearchResults(BaseModel):
    """
    A list of search results from a web search.

    Args:
        data: The list of search results
    """
    data: List[SearchResult]
