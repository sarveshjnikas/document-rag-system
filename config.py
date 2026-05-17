# config.py
from dotenv import load_dotenv
import os
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
LLM_MODEL = "gpt-4.1-mini"
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50