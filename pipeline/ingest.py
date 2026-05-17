# pipeline/ingest.py
import sys
from ingestion.loader import load_document
from ingestion.splitter import split_documents
from retrieval.vectorstore import build_store, reset_store

def ingest(path: str):
    print(f"Loading {path}...")
    docs = load_document(path)
    chunks = split_documents(docs)
    print(f"Split into {len(chunks)} chunks. Embedding...")
    build_store(chunks)
    print("Done.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise SystemExit("Usage: python -m pipeline.ingest [--reset] <path> [<path> ...]")

    args = sys.argv[1:]
    if args and args[0] == "--reset":
        reset_store()
        args = args[1:]

    if not args:
        raise SystemExit("Usage: python -m pipeline.ingest [--reset] <path> [<path> ...]")

    for p in args:
        ingest(p)
