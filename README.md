# WebSearch

Lightweight Python package for web search and clean content extraction using trafilatura. Designed for easy integration with LLM agents or custom projects.

## Installation

You can install this package directly from GitHub using pip:

```bash
pip install git+https://github.com/core-mfg/websearch.git
```

Or clone the repo and install in editable mode for development:

```bash
git clone https://github.com/core-mfg/websearch.git
cd websearch
pip install -e .
```

## Usage

### Synchronous Search

```python
from websearch.websearch import WebSearch

results = WebSearch.invoke("OpenAI GPT-4", max_results=3, fetch_content=True)
for result in results.data:
    print(f"Title: {result.title}")
    print(f"URL: {result.url}")
    print(f"Content snippet: {result.content[:200]}")
    print("-----")
```

### Asynchronous Search

```python
import asyncio
from websearch.websearch import WebSearch

async def main():
    results = await WebSearch.ainvoke("LangChain tutorial", fetch_content=False)
    for result in results.data:
        print(result.title, result.url)

asyncio.run(main())
```

## Integration with LangGraph Tools

You can also import ready-to-use tools for LangGraph or LLMs:

```python
from websearch.langgraph_tools import websearch, async_websearch

# Sync tool usage
results = websearch.invoke("Python async programming")

# Async tool usage
results = await async_websearch.ainvoke("Machine learning basics")
```

## Contributing

Feel free to open issues or PRs to improve the package!
