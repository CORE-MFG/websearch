from typing import Optional, Literal
from langchain_core.tools import tool
from websearch import WebSearch, Backends, SearchResults


@tool
def websearch(
    query: str,
    max_results: Optional[int] = None,
    fetch_content: Optional[bool] = False,
    safesearch: Optional[str] = "moderate",
    backend: Optional[Backends] = Backends.GOOGLE,
) -> SearchResults:
    """
    Perform a synchronous web search and return summarized results.

    Args:
        query: The search query
        max_results: The maximum number of results to return
        fetch_content: Whether to fetch content from the search results
        safesearch: The safesearch mode
        backend: The backend to use

    Returns:
        A dictionary containing the search results
    """
    return WebSearch.invoke(
        query=query,
        max_results=max_results,
        fetch_content=fetch_content,
        safesearch=safesearch,
        backend=backend,
    )


@tool
async def async_websearch(
    query: str,
    max_results: Optional[int] = None,
    fetch_content: Optional[bool] = False,
    safesearch: Optional[str] = "moderate",
    backend: Optional[Backends] = Backends.GOOGLE,
) -> SearchResults:
    """
    Perform an asynchronous web search and return summarized results.

    Args:
        query: The search query
        max_results: The maximum number of results to return
        fetch_content: Whether to fetch content from the search results
        safesearch: The safesearch mode
        backend: The backend to use

    Returns:
        A dictionary containing the search results
    """
    return await WebSearch.ainvoke(
        query=query,
        max_results=max_results,
        fetch_content=fetch_content,
        safesearch=safesearch,
        backend=backend,
    )
