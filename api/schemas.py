from pydantic import BaseModel

class QueryRequest(BaseModel):
    query: str

class Source(BaseModel):
    text: str
    score: float
    meta: dict = {}

class QueryResponse(BaseModel):
    answer: str
    sources: list[Source]
