from fastapi import FastAPI
from api.schemas import QueryRequest, QueryResponse
from pipeline.query import answer

app = FastAPI(title="document-qna")

@app.post("/query", response_model=QueryResponse)
def query(req: QueryRequest):
    result = answer(req.query)
    return QueryResponse(
        answer=result["answer"],
        sources=[{"text": s["text"], "score": s["score"]} for s in result["sources"]],
    )

@app.get("/health")
def health():
    return {"status": "ok"}
