# retrieval/retriever.py
from __future__ import annotations

import json
import sqlite3

import faiss
import numpy as np

import config
from ingestion.embedder import embed_texts


def _keyword_candidates(con: sqlite3.Connection, query: str, limit: int) -> list[dict]:
    tokens = [t for t in query.lower().replace("/", " ").split() if len(t) >= 3]
    if not tokens:
        return []

    # Pull candidate chunks by lexical match; keep it simple and small.
    like_clauses = " OR ".join(["lower(text) LIKE ?"] * min(len(tokens), 8))
    params = [f"%{t}%" for t in tokens[:8]]
    sql = f"SELECT id, text, meta FROM chunks WHERE {like_clauses} LIMIT ?"
    rows = con.execute(sql, (*params, limit)).fetchall()

    results: list[dict] = []
    for chunk_id, text, meta_json in rows:
        text_l = text.lower()
        score = sum(1 for t in tokens if t in text_l)
        results.append(
            {
                "id": int(chunk_id),
                "text": text,
                "meta": json.loads(meta_json) if meta_json else {},
                "score": float(score),
            }
        )
    results.sort(key=lambda r: r["score"], reverse=True)
    return results[:limit]


def retrieve(query: str, *, k: int | None = None) -> list[dict]:
    k = k or config.TOP_K
    index = faiss.read_index(config.VECTOR_STORE_PATH + ".faiss")

    q_vec = np.array(embed_texts([query]), dtype="float32")
    faiss.normalize_L2(q_vec)

    scores, ids = index.search(q_vec, k)

    con = sqlite3.connect(config.METADATA_DB_PATH)
    try:
        results: list[dict] = []
        seen_texts: set[str] = set()

        for score, chunk_id in zip(scores[0], ids[0]):
            if int(chunk_id) < 0:
                continue
            row = con.execute(
                "SELECT text, meta FROM chunks WHERE id=?", (int(chunk_id),)
            ).fetchone()
            if not row:
                continue
            text, meta_json = row
            if text in seen_texts:
                continue
            seen_texts.add(text)
            results.append(
                {
                    "text": text,
                    "meta": json.loads(meta_json) if meta_json else {},
                    "score": float(score),
                }
            )

        # Hybrid fallback: add a few lexical matches to help with tables / rare keywords.
        for cand in _keyword_candidates(con, query, limit=max(5, k)):
            if cand["text"] in seen_texts:
                continue
            seen_texts.add(cand["text"])
            results.append(
                {
                    "text": cand["text"],
                    "meta": cand["meta"],
                    # keep FAISS scores and keyword scores comparable by labeling keyword hits low.
                    "score": float(-1.0 * cand["score"]),
                }
            )

        return results[: max(k, 5)]
    finally:
        con.close()
