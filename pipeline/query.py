# pipeline/query.py
import config

from generation.llm import generate
from generation.prompt import build_prompt
from retrieval.retriever import retrieve

def answer(query: str) -> dict:
    chunks = retrieve(query, k=config.TOP_K)
    messages = build_prompt(query, chunks)
    response = generate(messages)
    return {
        "answer": response,
        "sources": [{"text": c["text"][:200], "meta": c["meta"], "score": c["score"]} for c in chunks],
    }
