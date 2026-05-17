# tests/test_vectorstore.py
from ingestion.loader import load_document
from ingestion.splitter import split_documents
from retrieval.vectorstore import build_store
import os


def test_build_store(tmp_path):
    chunks = split_documents(load_document("tests/fixtures/sample.txt"))

    def fake_embed(texts: list[str]) -> list[list[float]]:
        out = []
        for t in texts:
            v0 = float((hash(t) % 10_000) / 10_000)
            out.append([v0, 1.0 - v0, 0.1234])
        return out

    faiss_path, db_path = build_store(
        chunks,
        vector_store_path=str(tmp_path / "index"),
        metadata_db_path=str(tmp_path / "metadata.db"),
        embed_fn=fake_embed,
    )
    assert os.path.exists(faiss_path)
    assert os.path.exists(db_path)
