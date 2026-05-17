# tests/test_pipeline.py
import os
import pytest

from pipeline.query import answer

def test_end_to_end():
    if not os.getenv("OPENAI_API_KEY"):
        pytest.skip("OPENAI_API_KEY is not set")

    result = answer("summarise the key points of this document")
    print(result["answer"])
    print("---sources---")
    for s in result["sources"]:
        print(s["score"], s["meta"])
    assert len(result["answer"]) > 50
