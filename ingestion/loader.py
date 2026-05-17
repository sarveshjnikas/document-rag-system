from langchain_community.document_loaders import PyPDFLoader, TextLoader, UnstructuredHTMLLoader
from pathlib import Path

def load_document(path: str):
    ext = Path(path).suffix.lower()
    if ext == ".pdf":
        loader = PyPDFLoader(path)
    elif ext == ".txt":
        loader = TextLoader(path)
    elif ext in (".html", ".htm"):
        loader = UnstructuredHTMLLoader(path)
    else:
        raise ValueError(f"Unsupported file type: {ext}")
    
    return loader.load()   # returns list of Document objects