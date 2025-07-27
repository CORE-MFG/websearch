# Standard Library
import requests
from urllib.parse import urlparse
# Third Party
import trafilatura
# Core
from websearch import SearchResult, SearchResults
from websearch.logging import *


class WebScraper:
    """
    Industry-standard web content scraper using trafilatura for clean text extraction.
    
    This class provides methods to fetch and extract clean textual content from URLs
    typically returned by a search engine. It leverages `trafilatura` to remove
    boilerplate HTML and isolate meaningful content.

    Attributes:
        timeout (int): Maximum time (in seconds) to wait for a response.
        max_content_length (int): Upper limit on how much content (in characters) to process.
        session (requests.Session): Persistent HTTP session for efficient connections.
        logger: Configured logger instance.

    Example:
        ```python
        from websearch.scraper import WebScraper

        with WebScraper(timeout=5) as scraper:
            enriched = scraper.fetch_multiple(search_results)
        ```
    """
    
    def __init__(self, 
                 timeout: int = 10, 
                 max_content_length: int = 5000000,
                 logger_level: str = "INFO",
                 logger_enabled: bool = True,
        ):
        """
        Initialize the WebScraper with configuration parameters.

        Args:
            timeout (int): Request timeout in seconds.
            max_content_length (int): Maximum size of content (in bytes) to fetch per page.
            logger_level (str): Logging level ("DEBUG", "INFO", etc.).
            logger_enabled (bool): Whether logging is active.
        """
        self.timeout = timeout
        self.max_content_length = max_content_length
        self.session = requests.Session()
        
        # Set a realistic User-Agent to avoid blocking
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (compatible; WebSearchBot/1.0; +https://websearch.local/bot)'
        })

        self.logger = LoggerFactory.create_logger("WebScraper", logger_level, logger_enabled, "development")

    
    def fetch_content(self, search_result: SearchResult) -> SearchResult:
        """
        Fetch and extract cleaned textual content from a single URL in a SearchResult.

        Args:
            search_result (SearchResult): A single search result object containing a URL.

        Returns:
            SearchResult: A new SearchResult with extracted content in the `content` field.
                          If extraction fails, the original SearchResult is returned unmodified.
        """

        try:
            url = search_result.url.encoded_string()
            self.logger.info(f"Scraping content from: {url}")
            parsed = urlparse(url)
            self.logger.debug(f"Parsed URL to scrape: {parsed}")
            if not parsed.scheme or not parsed.netloc:
                self.logger.warning(f"Invalid URL format: {url}")
                return search_result
            
            # Fetch the webpage
            response = self.session.get(
                url, 
                timeout=self.timeout,
                allow_redirects=True,
                stream=True  # Use streaming to handle large files
            )
            try:
                response.raise_for_status()
            except requests.exceptions.HTTPError as e:
                self.logger.error(f"HTTP error {e.response.status_code} while fetching {url}")
                return search_result

            self.logger.debug(f"Response status code: {response.status_code}")
            
            # Check content type
            content_type = response.headers.get('content-type', '').lower()
            if 'text/html' not in content_type:
                self.logger.warning(f"Non-HTML content type for {url}: {content_type}")
                return search_result
            
            # Get content with size limit
            content = ""
            size = 0
            for chunk in response.iter_content(chunk_size=8192, decode_unicode=True):
                if chunk:
                    size += len(chunk)
                    if size > self.max_content_length:
                        self.logger.warning(f"Content too large for {url}, truncating at {self.max_content_length} chars")
                        break
                    content += chunk
            
            # Extract clean text using trafilatura
            extracted_text = trafilatura.extract(
                content,
                include_comments=False,
                include_tables=True,
                include_formatting=False,
                output_format='txt'
            )

            self.logger.debug(format_for_log(f"Extracted {len(extracted_text)} chars from {url}", extracted_text[:300] + "..."))
            
            if not extracted_text:
                self.logger.warning(f"No content extracted from {url}")
                return search_result
            
            # Basic cleaning - remove excessive whitespace
            cleaned_text = ' '.join(extracted_text.split())
            
            self.logger.info(f"Successfully extracted {len(cleaned_text)} characters from {url}")

            new_search_result = search_result.model_copy(update={"content": cleaned_text})
            return new_search_result
            
        except requests.exceptions.Timeout:
            self.logger.error(f"Timeout while fetching {url}")
            return search_result
        except requests.exceptions.ConnectionError:
            self.logger.error(f"Connection error while fetching {url}")
            return search_result
        except requests.exceptions.HTTPError as e:
            self.logger.error(f"HTTP error {e.response.status_code} while fetching {url}")
            return search_result
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Request error while fetching {url}: {str(e)}")
            return search_result
        except Exception as e:
            self.logger.error(f"Unexpected error while processing {url}: {str(e)}")
            return search_result
    
    def fetch_multiple(self, search_results: SearchResults) -> SearchResults:
        """
        Fetch content from multiple SearchResult objects and return enriched results.

        Args:
            search_results (SearchResults): A collection of search results to process.

        Returns:
            SearchResults: A new SearchResults object with each entry enriched
                           with extracted content if successful.
        """
        self.logger.info(
            format_for_log(
                f"Fetching content from {len(search_results.data)} URLs", 
                [f"{i}. {item.url.encoded_string()}" for i, item in enumerate(search_results.data)]
            )
        )

        new_results = search_results.model_copy(update={"data": []})
        for search_result in search_results.data:
            new_results.data.append(self.fetch_content(search_result))
        return new_results
    
    def close(self):
        """
        Release the HTTP session and free associated resources.
        Recommended when not using the context manager interface.
        """        
        self.session.close()
    
    def __enter__(self):
        """
        Enable context manager usage of WebScraper.

        Returns:
            WebScraper: The current instance.
        """
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Ensures the HTTP session is closed when exiting a context manager block.

        Args:
            exc_type: Exception type (if raised).
            exc_val: Exception value (if raised).
            exc_tb: Traceback object (if raised).
        """
        self.close()
