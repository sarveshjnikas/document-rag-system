import config
from generation.llm import generate, build_prompt
from retrieval.retriever import retrieve

def answer(query: str) -> dict:
    chunks = retrieve(query, k=config.TOP_K) # get the 5 most relevant chunks from the storage
    messages = build_prompt(query, chunks) # build the llm prompt, add the context to the query
    response = generate(messages) # get the actual response from the 
    return {
        "answer": response,
        "sources": chunks,
    }
