# generation/llm.py
from __future__ import annotations
from openai import OpenAI
import config

client = OpenAI(api_key=config.OPENAI_API_KEY)

def build_prompt(query: str, chunks: list[dict]) -> list[dict]:
    context = "\n\n---\n\n".join(c["text"] for c in chunks) 
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


def generate(messages: list[dict]) -> str:
    response = client.chat.completions.create(
        model=config.LLM_MODEL,
        messages=messages,
    )
    return response.choices[0].message.content