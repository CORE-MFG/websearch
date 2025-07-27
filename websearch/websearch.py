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
    A high-level web search utility using DuckDuckGo Search (DDGS) under the hood,
    optionally enriched with scraped page content via `WebScraper`.

    This class supports both synchronous and asynchronous invocation styles,
    making it suitable for a range of environments (e.g., CLI tools, web apps, agents).

    Class Attributes:
        api_key (str): Optional API key for future extension or authenticated engines.
        fetch_content (bool): If True, will scrape the content of each result URL.
        max_results (int): Default number of results to return if not explicitly specified.
        safesearch (str): Safe search filter. One of: "off", "moderate", "strict".
        backend (Backends): The default search backend to use (e.g., google, bing).

    Usage Example:
        results = WebSearch.invoke("latest robotics startups", fetch_content=True)
    """

    api_key: str = None
    fetch_content: bool = False
    max_results: int = 5
    safesearch: str = "moderate"
    backend: Backends = Backends.GOOGLE
    fetch_content_max_chars: int = 10000

    def __init__(self, log_level: str = "INFO", log_enabled: bool = False):
        """
        Initialize a WebSearch instance with logging preferences.

        Args:
            log_level (str): Logging level (e.g., "DEBUG", "INFO").
            log_enabled (bool): Whether to enable internal logging.
        """
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
                       fetch_content_max_chars: int = None,
                       safesearch: str = None, 
                       backend: Backends = None
        ) -> SearchResults:
        """
        Internal async method that performs the core search logic.

        Args:
            query (str): The search query string.
            max_results (int): Override the default number of results to fetch.
            fetch_content (bool): If True, scrape web pages for full content.
            fetch_content_max_chars (int): Maximum number of characters to fetch from each result.
            safesearch (str): Safe search mode for content filtering.
            backend (Backends): The search engine backend to use.

        Returns:
            SearchResults: A list of structured search results with optional full content.
        """
        max_results = max_results or self.max_results
        fetch_content = fetch_content or self.fetch_content
        fetch_content_max_chars = fetch_content_max_chars or self.fetch_content_max_chars
        safesearch = safesearch or self.safesearch
        backend = backend or self.backend

        self.logger.info(f"Searching for '{query}' on {backend}")
        self.logger.info(f"Config: max results = {max_results}, fetch content = {fetch_content}, w max chars = {fetch_content_max_chars}, safesearch = '{safesearch}'")

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
                    search_results = scraper.fetch_multiple(search_results, max_content_length=fetch_content_max_chars)

                self.logger.debug(format_for_log("WebScraper Results", search_results.model_dump()))

            return search_results

    @classmethod
    def invoke(cls, 
            query: str, 
            max_results: int = None, 
            fetch_content: bool = None, 
            fetch_content_max_chars: int = None,
            safesearch: str = None, 
            backend: Backends = None, 
            log_level: str = None, 
            log_enabled: bool = None
        ) -> SearchResults:
        """
        Synchronous interface to perform a blocking web search.

        Args:
            query (str): The search query.
            max_results (int): Max number of results (overrides class default).
            fetch_content (bool): Whether to scrape each result’s page.
            fetch_content_max_chars (int): Maximum number of characters to fetch from each result.
            safesearch (str): Safesearch filtering level.
            backend (Backends): Search backend to use.
            log_level (str): Optional log level override.
            log_enabled (bool): Optional logging toggle.

        Returns:
            SearchResults: Structured, optionally enriched search results.
        """
        instance = cls(log_level, log_enabled)
        return asyncio.run(instance._ainvoke(query, max_results, fetch_content, fetch_content_max_chars, safesearch, backend))

    @classmethod
    async def ainvoke(cls, 
            query: str, 
            max_results: int = None, 
            fetch_content: bool = None,
            fetch_content_max_chars: int = None,
            safesearch: str = None, 
            backend: Backends = None,
            log_level: str = "INFO", 
            log_enabled: bool = False
        ) -> SearchResults:
        """
        Asynchronous interface to perform a non-blocking web search.

        Args:
            query (str): The search query.
            max_results (int): Max number of results (overrides class default).
            fetch_content (bool): Whether to scrape each result’s page.
            fetch_content_max_chars (int): Maximum number of characters to fetch from each result.
            safesearch (str): Safesearch filtering level.
            backend (Backends): Search backend to use.
            log_level (str): Optional log level override.
            log_enabled (bool): Optional logging toggle.

        Returns:
            SearchResults: Structured, optionally enriched search results.
        """
        instance = cls(log_level, log_enabled)
        return await instance._ainvoke(query, max_results, fetch_content, fetch_content_max_chars, safesearch, backend)