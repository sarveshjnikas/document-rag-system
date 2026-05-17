# generation/prompt.py
def build_prompt(query: str, chunks: list[dict]) -> list[dict]:
    context = "\n\n---\n\n".join(c["text"] for c in chunks)
    answer_format = ""
    if "one number" in query.lower() or "give one number" in query.lower():
        answer_format = (
            "\n\nOutput format requirement:\n"
            "- Return exactly one number (optionally with ₹ or $), and nothing else.\n"
            "- Use only a number that appears verbatim in the context.\n"
        )
    return [
        {
            "role": "system",
            "content": (
                "You are a helpful assistant. Answer the user's question using only "
                "the context provided below. If the answer is not in the context, say "
                "'I don't know based on the provided documents'."
                f"{answer_format}\n\n"
                f"Context:\n{context}"
            ),
        },
        {"role": "user", "content": query},
    ]
