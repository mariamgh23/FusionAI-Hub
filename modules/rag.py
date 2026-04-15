"""RAG: ingest text chunks into an in-memory store, then retrieve + answer."""
from __future__ import annotations
import re
from utils.llm import chat, embed

# Simple in-process vector store (list of {text, vector})
_store: list[dict] = []


def _cosine(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    na  = sum(x ** 2 for x in a) ** 0.5
    nb  = sum(x ** 2 for x in b) ** 0.5
    return dot / (na * nb + 1e-9)


def ingest(text: str, chunk_size: int = 500) -> int:
    """Split text into chunks and store with embeddings. Returns chunk count."""
    words  = text.split()
    chunks = [" ".join(words[i:i+chunk_size]) for i in range(0, len(words), chunk_size)]
    for chunk in chunks:
        try:
            vec = embed(chunk)
            _store.append({"text": chunk, "vector": vec})
        except Exception:
            _store.append({"text": chunk, "vector": []})
    return len(chunks)


def retrieve(query: str, top_k: int = 4) -> list[str]:
    if not _store:
        return []
    try:
        q_vec = embed(query)
        scored = sorted(_store, key=lambda d: _cosine(q_vec, d["vector"]) if d["vector"] else -1, reverse=True)
        return [d["text"] for d in scored[:top_k]]
    except Exception:
        return [d["text"] for d in _store[:top_k]]


def run_rag(query: str) -> str:
    if not _store:
        return "⚠️ No documents ingested yet. Please upload and ingest a file first."
    context = "\n\n".join(retrieve(query))
    system  = "You are a helpful assistant. Answer using ONLY the provided context."
    prompt  = f"Context:\n{context}\n\nQuestion: {query}"
    return chat(prompt, system)


def clear_store():
    _store.clear()


def store_size() -> int:
    return len(_store)
