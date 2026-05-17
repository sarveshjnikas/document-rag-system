# generation/llm.py
from openai import OpenAI
import config

client = OpenAI(api_key=config.OPENAI_API_KEY)

def generate(messages: list[dict]) -> str:
    response = client.chat.completions.create(
        model=config.LLM_MODEL,
        messages=messages,
    )
    return response.choices[0].message.content