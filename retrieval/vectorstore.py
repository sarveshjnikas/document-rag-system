from __future__ import annotations

import json
import sqlite3
from pathlib import Path

import faiss
import numpy as np
from ingestion.embedder import embed_texts
import config


# Deletes existing vector and metadata storage.
def reset_store(*,
    vector_store_path: str | None = None,
    metadata_db_path: str | None = None,
) -> None:
    vector_store_path = vector_store_path or config.VECTOR_STORE_PATH
    metadata_db_path = metadata_db_path or config.METADATA_DB_PATH

    vector_store_faiss_path = Path(vector_store_path).with_suffix(".faiss")
    metadata_db_file = Path(metadata_db_path)

    if vector_store_faiss_path.exists():
        vector_store_faiss_path.unlink()
    if metadata_db_file.exists():
        metadata_db_file.unlink()


# Opens (or creates) the SQLite database file and ensures the chunks table exists before returning the database connection.
def _open_db(metadata_db_path: str) -> sqlite3.Connection:
    con = sqlite3.connect(metadata_db_path)
    con.execute(
        "CREATE TABLE IF NOT EXISTS chunks (id INTEGER PRIMARY KEY, text TEXT, meta TEXT)"
    )
    return con


# get the id of the next chunk to be inserted
def _next_chunk_id(con: sqlite3.Connection) -> int:
    row = con.execute("SELECT COALESCE(MAX(id), 0) FROM chunks").fetchone()
    return int(row[0] or 0) + 1


# Checks that the FAISS index can store and retrieve vectors using your own IDs, so they stay linked to the correct text chunks in the database.
def _ensure_idmap_index(index: faiss.Index) -> faiss.Index:
    if isinstance(index, faiss.IndexIDMap) or isinstance(index, faiss.IndexIDMap2):
        return index
    raise ValueError(
        "Existing FAISS index is not ID-mapped. "
        "Reset the store (delete store/index.faiss and store/metadata.db) and rebuild."
    )


def build_store(
    chunks,
    *,
    vector_store_path: str | None = None,
    metadata_db_path: str | None = None,
) -> tuple[str, str]:

    # Embedding model only needs raw text. SQLite needs metadata. separate concerns
    texts = [c.page_content for c in chunks]
    metas = [c.metadata for c in chunks]

    vector_store_path = vector_store_path or config.VECTOR_STORE_PATH
    metadata_db_path = metadata_db_path or config.METADATA_DB_PATH
    vector_store_faiss_path = str(Path(vector_store_path).with_suffix(".faiss"))

    Path(vector_store_faiss_path).parent.mkdir(parents=True, exist_ok=True)
    Path(metadata_db_path).parent.mkdir(parents=True, exist_ok=True)

    # Opens (or creates) the SQLite database file and ensures the chunks table exists before returning the database connection.
    con = _open_db(metadata_db_path)
    try:
        start_id = _next_chunk_id(con)
        vectors: list[list[float]] = []
        
        # take all text chunks, processes them in batches of 100, converts each batch into embeddings, and collects all embeddings into one list.
        for i in range(0, len(texts), 100):
            vectors.extend(embed_texts(texts[i : i + 100]))

        # normalize --> later while searching we need to do the same
        dim = len(vectors[0])
        vecs = np.array(vectors, dtype="float32")
        faiss.normalize_L2(vecs)

        # Creates unique numeric IDs for every text chunk.
        ids = np.arange(start_id, start_id + len(texts), dtype="int64")

        index_path = Path(vector_store_faiss_path)
        if index_path.exists():
            # Loads the existing FAISS index from disk and makes sure it supports custom IDs.
            index = _ensure_idmap_index(faiss.read_index(vector_store_faiss_path))
            # Were old vectors created using same embedding model?
            if index.d != dim:
                raise ValueError(
                    f"Embedding dimension mismatch (index dim={index.d}, new dim={dim}). "
                    "Reset the store and rebuild."
                )
        else:
            index = faiss.IndexIDMap2(faiss.IndexFlatIP(dim))

        # Store embeddings in vector DB with their IDs.
        index.add_with_ids(vecs, ids)
        faiss.write_index(index, vector_store_faiss_path) # Persist vector DB to file.

        con.executemany(
            "INSERT INTO chunks (id, text, meta) VALUES (?, ?, ?)",
            [(int(i), t, json.dumps(m)) for i, t, m in zip(ids, texts, metas)],
        )
        con.commit()
    finally:
        con.close()

    return vector_store_faiss_path, metadata_db_path
