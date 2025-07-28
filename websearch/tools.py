# ./websearch/tools.py

from typing import Optional
from langchain_core.tools import tool
from websearch import WebSearch, Backends, SearchResults


@tool
def websearch(
    query: str,
    max_results: Optional[int] = None,
    fetch_content: Optional[bool] = False,
    fetch_content_max_chars: Optional[int] = None,
    safesearch: Optional[str] = "moderate",
    backend: Optional[Backends] = Backends.GOOGLE,
) -> dict:
    """
    Perform a synchronous web search and return summarized results.

    This tool queries a search engine and returns a list of relevant results, 
    optionally with fetched page content. Useful for real-time knowledge retrieval.

    Args:
        query (str): The search query string (e.g., "latest AI research").
        max_results (Optional[int]): Maximum number of search results to return. 
            If None, a default limit is applied by the backend.
        fetch_content (Optional[bool]): If True, fetches the page content from each result URL. 
            This enables deeper summarization and downstream parsing.
        fetch_content_max_chars (Optional[int]): Maximum number of characters to fetch from each result.
        safesearch (Optional[str]): Controls content filtering.
            One of: "off", "moderate" (default), or "strict".
        backend (Optional[Backends]): The backend search engine to use.
            Options may include GOOGLE, BING, DDG, etc.

    Returns:
        SearchResults: A structured object containing metadata and optional content
        for each search result.
    """
    results: SearchResults = WebSearch.invoke(
        query=query,
        max_results=max_results,
        fetch_content=fetch_content,
        fetch_content_max_chars=fetch_content_max_chars,
        safesearch=safesearch,
        backend=backend,
    )
    return results.model_dump()


@tool
async def async_websearch(
    query: str,
    max_results: Optional[int] = None,
    fetch_content: Optional[bool] = False,
    fetch_content_max_chars: Optional[int] = None,
    safesearch: Optional[str] = "moderate",
    backend: Optional[Backends] = Backends.GOOGLE,
) -> SearchResults:
    """
    Perform an asynchronous web search and return summarized results.

    This non-blocking variant enables concurrent workflows, such as when
    coordinating multiple web tools or agents.

    Args:
        query (str): The search query string (e.g., "economic outlook 2025").
        max_results (Optional[int]): Maximum number of results to return. 
            If None, the backend's default limit is used.
        fetch_content (Optional[bool]): If True, fetches the page content for each result.
        fetch_content_max_chars (Optional[int]): Maximum number of characters to fetch from each result.
        safesearch (Optional[str]): Controls filtering for adult or explicit content.
            Valid values: "off", "moderate" (default), "strict".
        backend (Optional[Backends]): The search engine backend to query. 
            Defaults to Backends.GOOGLE.

    Returns:
        SearchResults: A structured object containing titles, URLs, snippets,
        and optionally, full page content for each result.
    """
    results: SearchResults = await WebSearch.ainvoke(
        query=query,
        max_results=max_results,
        fetch_content=fetch_content,
        fetch_content_max_chars=fetch_content_max_chars,
        safesearch=safesearch,
        backend=backend,
    )
    return results.model_dump()
