# pipeline/ingest.py
import sys
from ingestion.loader import load_document
from ingestion.splitter import split_documents
from retrieval.vectorstore import build_store

def ingest(path: str):
    print(f"Loading {path}...")
    docs = load_document(path)
    chunks = split_documents(docs)
    print(f"Split into {len(chunks)} chunks. Embedding...")
    build_store(chunks)
    print("Done.")

if __name__ == "__main__":
    ingest(sys.argv[1])