from __future__ import annotations

import json
import sqlite3
from collections.abc import Callable
from pathlib import Path

import faiss
import numpy as np

import config


def build_store(
    chunks,
    *,
    vector_store_path: str | None = None,
    metadata_db_path: str | None = None,
    embed_fn: Callable[[list[str]], list[list[float]]] | None = None,
) -> tuple[str, str]:
    texts = [c.page_content for c in chunks]
    metas = [c.metadata for c in chunks]

    if embed_fn is None:
        from ingestion.embedder import embed_texts
        embed_fn = embed_texts

    all_vecs = []
    for i in range(0, len(texts), 100):
        all_vecs.extend(embed_fn(texts[i : i + 100]))

    dim = len(all_vecs[0])

    index = faiss.IndexFlatIP(dim)
    vecs = np.array(all_vecs, dtype="float32")
    faiss.normalize_L2(vecs)
    index.add(vecs)

    vector_store_path = vector_store_path or config.VECTOR_STORE_PATH
    metadata_db_path = metadata_db_path or config.METADATA_DB_PATH
    vector_store_faiss_path = str(Path(vector_store_path).with_suffix(".faiss"))

    Path(vector_store_faiss_path).parent.mkdir(parents=True, exist_ok=True)
    Path(metadata_db_path).parent.mkdir(parents=True, exist_ok=True)

    faiss.write_index(index, vector_store_faiss_path)

    con = sqlite3.connect(metadata_db_path)

    con.execute(
        "CREATE TABLE IF NOT EXISTS chunks (id INTEGER PRIMARY KEY, text TEXT, meta TEXT)"
    )

    con.executemany(
        "INSERT INTO chunks (text, meta) VALUES (?, ?)",
        [(t, json.dumps(m)) for t, m in zip(texts, metas)]
    )

    con.commit()
    con.close()

    return vector_store_faiss_path, metadata_db_path
