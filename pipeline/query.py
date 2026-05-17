# pipeline/query.py
from retrieval.retriever import retrieve
from generation.prompt import build_prompt
from generation.llm import generate
import config

def answer(query: str) -> dict:
    chunks = retrieve(query, k=max(config.TOP_K, 15))
    messages = build_prompt(query, chunks)
    response = generate(messages)
    return {
        "answer": response,
        "sources": [{"text": c["text"][:200], "meta": c["meta"], "score": c["score"]} for c in chunks],
    }
