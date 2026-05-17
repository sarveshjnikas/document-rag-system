# tests/test_retrieval.py
import os
import pytest

from retrieval.retriever import retrieve

def test_retrieval_relevance():
    if not os.getenv("OPENAI_API_KEY"):
        pytest.skip("OPENAI_API_KEY is not set")

    query = "para"   # use something specific to your PDF
    results = retrieve(query)
    assert len(results) == 5
    for r in results:
        print(f"score={r['score']:.3f} | {r['text'][:120]}")
