# websearch/websearch.py

# Standard Library
import asyncio
from enum import Enum
from typing import Literal
# Third Party
import httpx
from ddgs import DDGS
from ddgs.engines import ENGINES
# Core
from websearch import SearchResult, SearchResults, WebScraper
from websearch.logging import LoggerFactory, format_for_log


class Backends(str, Enum):
    DUCKDUCKGO = "duckduckgo"
    GOOGLE = "google"
    BING = "bing"
    BRAVE = "brave"
    YAHOO = "yahoo"
    YANDEX = "yandex"

class WebSearch:
    """
    WebSearch class for searching the web.

    Args:
        api_key: API key for the search engine
        fetch_content: Whether to fetch content from the search results
        max_results: Maximum number of results to return
        safesearch: Safesearch mode
    """

    api_key: str = None
    fetch_content: bool = False
    max_results: int = 5
    safesearch: str = "moderate"
    backend: Backends = Backends.GOOGLE

    def __init__(self, log_level: str = "INFO", log_enabled: bool = False):
        self.logger = LoggerFactory.create_logger(
            "WebSearch",
            log_level,
            log_enabled,
            "development"
        )

    async def _ainvoke(self, 
                       query: str, 
                       max_results: int = None, 
                       fetch_content: bool = None, 
                       safesearch: str = None, 
                       backend: Backends = None
        ) -> SearchResults:
        """Internal async logic shared by both interfaces."""
        max_results = max_results or self.max_results
        fetch_content = fetch_content or self.fetch_content
        safesearch = safesearch or self.safesearch
        backend = backend or self.backend

        self.logger.info(f"Searching for '{query}' on {backend}")
        self.logger.info(f"Config: max results = {max_results}, fetch content = {fetch_content}, safesearch = '{safesearch}'")

        async with httpx.AsyncClient() as client:
            # Get search results
            with DDGS() as ddgs:
                raw_ddgs_search_results = ddgs.text(
                    query, safesearch=safesearch, max_results=max_results, backend=backend
                )

            self.logger.info(f"Fetched {len(raw_ddgs_search_results)} results from {self.backend}")
            self.logger.debug(format_for_log("Raw DDGS Search Results", raw_ddgs_search_results))

            search_results : SearchResults = SearchResults(data=[])

            # Convert to SearchResults
            for result in raw_ddgs_search_results:
                search_results.data.append(SearchResult(
                    url=result.get("href"),
                    title=result.get("title") or "no title from ddgs",
                    snippet=result.get("body") or "no body from ddgs",
                    content=result.get("body") or "no body from ddgs"
                ))

            self.logger.debug(format_for_log("DDGS SearchResults", search_results.model_dump()))

            # Convert each SearchResult to dict and collect in a list
            # results_as_dicts = [result.model_dump() for result in search_results.results]

            if fetch_content:
                # Fetch content from each URL
                self.logger.info("Scraping content for search results...")
                with WebScraper() as scraper:
                    search_results = scraper.fetch_multiple(search_results)

                self.logger.debug(format_for_log("WebScraper Results", search_results.model_dump()))

            return search_results

    @classmethod
    def invoke(cls, 
            query: str, 
            max_results: int = None, 
            fetch_content: bool = None, 
            safesearch: str = None, 
            backend: Backends = None, 
            log_level: str = None, 
            log_enabled: bool = None
        ) -> SearchResults:
        """Sync interface for blocking codebases."""
        instance = cls(log_level, log_enabled)
        return asyncio.run(instance._ainvoke(query, max_results, fetch_content, safesearch, backend))

    @classmethod
    async def ainvoke(cls, 
            query: str, 
            max_results: int = None, 
            fetch_content: bool = None, 
            safesearch: str = None, 
            backend: Backends = None,
            log_level: str = None, 
            log_enabled: bool = None
        ) -> SearchResults:
        """Async interface for async codebases."""
        instance = cls(log_level, log_enabled)
        return await instance._ainvoke(query, max_results, fetch_content, safesearch, backend)