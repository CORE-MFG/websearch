# run.py

# Standard Library
from pprint import pprint
# Core
from websearch.logging import *
from websearch.websearch import Backends, WebSearch

logger = LoggerFactory.create_logger("Run", "DEBUG", True, "development")

def test_websearch_invoke():
    query = "open source LLM observability tools"
    result = WebSearch.invoke(
        query=query, 
        max_results=5, 
        fetch_content=True, 
        safesearch="moderate", 
        backend=Backends.GOOGLE, 
        log_level="INFO",
        log_enabled=False    
    )

    for i, res in enumerate(result.data, 1):
        logger.info(f"{i}. {len(res.content)} \t chars from '{res.title[:30]}...' - {res.url}")

if __name__ == "__main__":
    test_websearch_invoke()
