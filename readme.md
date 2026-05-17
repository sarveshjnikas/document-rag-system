The primary goal of this project is to learn about RAG systems, vector databases, and adjascent concepts while building a (hopefully) useful project.

Problem:
If we have a huge pile of documents — hundreds of PDFs, articles, notes. An LLM on its own can't read all of them (too long, and it forgets them after the conversation ends). So we need a smarter approach.

Part 1: Prepare the library (ingestion). We do this once, upfront.
Take every document, cut it into small chunks (like paragraphs), and for each chunk you run it through an embedding model — which converts text into a list of numbers (a "vector") that captures its meaning. All these vectors get stored in a vector store — basically a database optimised for finding similar vectors fast.

Part 2: Answer a question (query). This happens every time a user asks something.
Take the user's question, run it through the exact same embedding model to get its vector, then search the vector store for the chunks whose vectors are closest — these are the most relevant passages. You then stuff those passages + the original question into a prompt and hand it to the LLM. The LLM reads the pasted-in context and writes an answer grounded in it.