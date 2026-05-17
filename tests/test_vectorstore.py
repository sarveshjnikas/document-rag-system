# tests/test_vectorstore.py
from ingestion.loader import load_document
from ingestion.splitter import split_documents
from retrieval.vectorstore import build_store
import os
import sqlite3


def test_build_store(tmp_path):
    chunks = split_documents(load_document("tests/fixtures/fees_structure_2026_admission_ug_pg.pdf"))

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

    # Second build should append (not overwrite).
    faiss_path_2, db_path_2 = build_store(
        chunks[:5],
        vector_store_path=str(tmp_path / "index"),
        metadata_db_path=str(tmp_path / "metadata.db"),
        embed_fn=fake_embed,
    )
    assert faiss_path_2 == faiss_path
    assert db_path_2 == db_path

    con = sqlite3.connect(db_path)
    try:
        count = con.execute("select count(*) from chunks").fetchone()[0]
    finally:
        con.close()
    assert count == len(chunks) + 5
