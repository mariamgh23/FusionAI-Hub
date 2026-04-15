import requests
from utils.config import OLLAMA_BASE_URL, OLLAMA_CHAT_MODEL, OLLAMA_EMBED_MODEL

def chat(prompt: str, system: str = "") -> str:
    """Send a prompt to Ollama; return text response."""
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    try:
        r = requests.post(
            f"{OLLAMA_BASE_URL}/api/chat",
            json={"model": OLLAMA_CHAT_MODEL, "messages": messages, "stream": False},
            timeout=60,
        )
        r.raise_for_status()
        return r.json()["message"]["content"]
    except Exception as e:
        return f"[LLM Error] {e}\n\n(Is Ollama running? `ollama serve`)"


def embed(text: str) -> list[float]:
    """Return embedding vector for text."""
    try:
        r = requests.post(
            f"{OLLAMA_BASE_URL}/api/embeddings",
            json={"model": OLLAMA_EMBED_MODEL, "prompt": text},
            timeout=30,
        )
        r.raise_for_status()
        return r.json()["embedding"]
    except Exception as e:
        raise RuntimeError(f"Embedding failed: {e}")


def ollama_available() -> bool:
    try:
        r = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5)
        return r.status_code == 200
    except Exception:
        return False
