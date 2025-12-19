from typing import List, Optional
from pydantic import BaseModel

class QueryRequest(BaseModel):
    query: str

class Citation(BaseModel):
    source: str
    page: Optional[int] = None
    text_snippet: Optional[str] = None

class QueryResponse(BaseModel):
    answer: str
    citations: List[Citation]

class IngestResponse(BaseModel):
    message: str
    num_documents: int
