from ingestion.loader import load_document
from ingestion.splitter import split_documents

def test_load_and_split():
    docs = load_document("tests/fixtures/sample.txt")
    assert len(docs) > 0

    chunks = split_documents(docs)
    assert len(chunks) >= len(docs)
    assert len(chunks[0].page_content) <= 600   # rough size sanity check
    print(f"chunks: {len(chunks)}, first chunk preview: {chunks[0].page_content[:100]}")    
