The primary goal of this project is to learn about RAG systems, vector databases, and adjascent concepts while building a (hopefully) useful project.

Problem:
If we have a huge pile of documents — hundreds of PDFs, articles, notes. An LLM on its own can't read all of them (too long, and it forgets them after the conversation ends). So we need a smarter approach.

Part 1: Prepare the library (ingestion). We do this once, upfront.
Take every document, cut it into small chunks (like paragraphs), and for each chunk you run it through an embedding model — which converts text into a list of numbers (a "vector") that captures its meaning. All these vectors get stored in a vector store — basically a database optimised for finding similar vectors fast.

Part 2: Answer a question (query). This happens every time a user asks something.
Take the user's question, run it through the exact same embedding model to get its vector, then search the vector store for the chunks whose vectors are closest — these are the most relevant passages. You then stuff those passages + the original question into a prompt and hand it to the LLM. The LLM reads the pasted-in context and writes an answer grounded in it.

The flow diagram would look something like:

Documents — the raw source files you feed in.

Document loader — reads those files and extracts plain text plus metadata (filename, page number, URL). Handles format differences so the rest of the pipeline sees clean, uniform text regardless of the source.

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
