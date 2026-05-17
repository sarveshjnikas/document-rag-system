# Document QnA (RAG)

Learn RAG systems and vector databases by building a small document Q&A project.

## Problem

If we have a huge pile of documents—hundreds of PDFs, articles, notes—an LLM on its own can’t read all of them (too long, and it forgets them after the conversation ends). So we need a smarter approach.

## Approach

### Part 1: Prepare the library (ingestion)

Do this once, upfront:
- Take each document and split it into small chunks (like paragraphs).
- Run each chunk through an embedding model to convert text into a vector (a list of numbers capturing meaning).
- Store all vectors in a vector store (optimized for fast similarity search).

### Part 2: Answer a question (query)

This happens every time a user asks something:
- Embed the user’s question using the **same** embedding model.
- Search the vector store for the closest chunk vectors (most relevant passages).
- Provide the retrieved passages + the question to the LLM so it answers grounded in the documents.

## Components (at a glance)

- **Documents** — raw source files you feed in.
- **Document loader** — reads files and extracts plain text + metadata (filename, page, URL).
- **Text splitter** — breaks long documents into smaller overlapping chunks.
- **Embedding model** — converts text to vectors (used at ingestion and query time; must match).
- **Vector store** — stores vectors and supports nearest-neighbor search (FAISS / Pinecone / Weaviate).
- **Retriever** — returns top‑k chunks most similar to the query vector (cosine similarity).
- **Prompt builder** — assembles system instruction + retrieved context + question.
- **LLM** — generates the final answer using the provided context (reduces hallucinations).

## Flow Diagram

Text splitter — breaks long documents into smaller overlapping chunks. Overlap ensures no sentence gets stranded at a boundary. Smaller chunks are what the embedding model and retrieval step actually operate on.

Embedding model — turns a piece of text into a list of numbers (a vector). The key property is that similar meanings produce similar vectors. Used twice: once at ingestion to encode every chunk, once at query time to encode the user's question. Must be the same model both times.

Vector store — a database built specifically for storing and searching vectors. Holds every chunk alongside its embedding. When a query vector comes in, it finds the closest matching chunk vectors using approximate nearest neighbour search. FAISS, Pinecone, and Weaviate are common choices.

Retriever — sends the query vector into the vector store and gets back the top-k most similar chunks. This is the actual search step — similarity is measured by cosine distance between vectors.

Prompt builder — assembles the final prompt: a system instruction, the retrieved chunks pasted in as context, and the original question. This is what keeps the LLM grounded — it can only see what was retrieved.

LLM — reads the assembled prompt and generates an answer in natural language. Because the relevant text is right there in the context window, it doesn't have to rely on memorised training data, which is why RAG reduces hallucinations.

Answer — the final response.
```text
┌─────────────────────────────────────────────────────────────────────────┐
│                         INGESTION PIPELINE                              │
│                                                                         │
│   ┌─────────────┐    ┌─────────────┐    ┌─────────────┐                 │
│   │  Documents  │───▶│   Document  │───▶│    Text     │                 │
│   │ PDF·HTML·   │    │   loader    │    │   splitter  │                 │
│   │    DOCX     │    │             │    │  (chunker)  │                 │
│   └─────────────┘    └─────────────┘    └──────┬──────┘                 │
│                                                 │                       │
│                                                 ▼                       │
│                                         ┌─────────────┐                 │
│                                         │  Embedding  │                 │
│                                         │    model    │                 │
│                                         │ chunk→vec   │                 │
│                                         └──────┬──────┘                 │
│                                                 │                       │
└─────────────────────────────────────────────────┼───────────────────────┘
                                                  │
                                                  ▼
                                        ╔═════════════════╗
                                        ║  Vector store   ║
                                        ║ FAISS·Pinecone  ║
                                        ║    Weaviate     ║
                                        ╚════════╤════════╝
                                                 │
┌────────────────────────────────────────────────┼───────────────────────┐
│                        QUERY PIPELINE          │                       │
│                                                │                       │
│   ┌─────────────┐    ┌─────────────┐           │ top-k chunks          │
│   │ User query  │───▶│  Embedding  │───────────┤                       │
│   │             │    │ query→vec   │ search     ▼                      │
│   │             │    │    model    │ cosine     │                      │
│   │             │    └─────────────┘    ┌─────────────┐                │
│   │             │                       │  Retriever  │                │
│   │             │                       └──────┬──────┘                │
│   │             │                              │                       │
│   │             │──────────────────────────────┤                       │
│   └─────────────┘   original question          │                       │
│                                                ▼                       │
│                                        ┌─────────────┐                 │
│                                        │   Prompt    │                 │
│                                        │   builder   │                 │
│                                        │context+query│                 │
│                                        └──────┬──────┘                 │
│                                               │                         │
│                                               ▼                       │
│                                        ┌─────────────┐               │
│                                        │     LLM     │               │
│                                        │  grounded   │               │
│                                        │ generation  │               │
│                                        └──────┬──────┘               │
│                                               │                       │
│                                               ▼                       │
│                                        ┌─────────────┐               │
│                                        │   Answer    │               │
│                                        └─────────────┘               │
└────────────────────────────────────────────────────────────────────────┘
```

## Run It

### 1) Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Set your API key (either in `.env` or your shell):

```bash
export OPENAI_API_KEY="YOUR_KEY_HERE"
```

### 2) Ingest (build the store)

This creates/overwrites `store/index.faiss` and `store/metadata.db`.

```bash
python -m pipeline.ingest tests/fixtures/fees_structure_2026_admission_ug_pg.pdf
```

### 3) Run the API

```bash
uvicorn api.main:app --reload
```

Open:
- `http://127.0.0.1:8000/docs` (Swagger UI)
- `http://127.0.0.1:8000/health`

### 4) Ask a question

```bash
curl -s -X POST "http://127.0.0.1:8000/query" \
  -H "Content-Type: application/json" \
  -d '{"query":"What are the fees for MBA for foreign nationals?"}'
```

### 5) Run tests

```bash
pytest -q
```
