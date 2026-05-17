from __future__ import annotations

# generation/prompt.py
def build_prompt(query: str, chunks: list[dict]) -> list[dict]:
    max_chunks = 5
    max_chars_per_chunk = 800
    context = "\n\n---\n\n".join(
        c["text"][:max_chars_per_chunk] for c in chunks[:max_chunks]
    )
    return [
        {
            "role": "system",
            "content": (
                "You are a helpful assistant. Answer the user's question using only "
                "the context provided below. If the answer is not in the context, say "
                "'I don't know based on the provided documents'.\n\n"
                f"Context:\n{context}"
            ),
        },
        {"role": "user", "content": query},
    ]
