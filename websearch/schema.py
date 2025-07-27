# Standard Library
from typing import List
# Third Party
from pydantic import BaseModel, HttpUrl


class SearchResult(BaseModel):
    url: HttpUrl
    title: str
    snippet: str
    content: str

class SearchResults(BaseModel):
    data: List[SearchResult]
