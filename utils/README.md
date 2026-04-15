# 🛠️ utils/

Shared utility layer used by all feature modules. Contains the Ollama client wrapper and the centralized configuration registry.

---

## Files

| File | Purpose |
|------|---------|
| [`llm.py`](#llmpy) | Ollama REST API client — chat, embeddings, health check |
| [`config.py`](#configpy) | Environment-based configuration with safe defaults |

---

## llm.py

A thin wrapper around [Ollama's REST API](https://github.com/ollama/ollama/blob/main/docs/api.md). All three functions are used across every feature module.

### Functions

```python
chat(prompt: str, system: str = "") -> str
```

Sends a prompt to the configured Ollama chat model and returns the response text.

- Builds a `messages` array — prepends a system message if `system` is provided
- Uses `POST /api/chat` with `stream: false`
- 60-second timeout
- Returns a user-friendly error string (not an exception) on failure, so the UI never crashes

**Example:**
```python
from utils.llm import chat

answer = chat("What is the capital of France?", system="Answer in one word.")
# → "Paris"
```

---

```python
embed(text: str) -> list[float]
```

Returns the embedding vector for `text` using the configured embed model.

- Uses `POST /api/embeddings`
- 30-second timeout
- **Raises `RuntimeError`** on failure (unlike `chat`, callers handle this explicitly)
- Default model produces 384-dimensional vectors

**Example:**
```python
from utils.llm import embed

vector = embed("enterprise AI platform")
# → [0.023, -0.145, 0.087, ...]  # 384 floats
```

---

```python
ollama_available() -> bool
```

Lightweight health check. Hits `GET /api/tags` with a 5-second timeout.
Returns `True` if Ollama is reachable and responding, `False` otherwise.
Used by `app.py` to display the connection status indicator in the sidebar.

**Example:**
```python
from utils.llm import ollama_available

if not ollama_available():
    print("Start Ollama first: ollama serve")
```

---

### Error handling

`chat()` catches all exceptions and returns an informative string instead of raising:

```
[LLM Error] Connection refused

(Is Ollama running? `ollama serve`)
```

This keeps the Streamlit UI functional even when Ollama is temporarily unavailable.

---

## config.py

Central registry for all configuration values. Every setting reads from an environment variable with a safe local-development default.

### LLM Settings

| Variable | Default | Description |
|----------|---------|-------------|
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama server base URL |
| `OLLAMA_CHAT_MODEL` | `llama3.1:8b` | Chat / instruction model |
| `OLLAMA_EMBED_MODEL` | `nomic-embed-text` | Embedding model |

### Elasticsearch / Vector Store

| Variable | Default | Description |
|----------|---------|-------------|
| `ES_HOST` | `http://localhost:9200` | Elasticsearch / CSS host |
| `ES_USERNAME` | `admin` | Auth username |
| `ES_PASSWORD` | `admin` | Auth password |
| `ES_RAG_INDEX` | `nas_knowledge` | RAG knowledge index name |
| `ES_SECURITY_INDEX` | `nas_security_logs` | Security log index name |
| `VECTOR_DIMS` | `384` | Embedding dimension (must match model output) |

### Database (Analytics AI)

| Variable | Default | Description |
|----------|---------|-------------|
| `DB_TYPE` | `sqlite` | Database type (`sqlite` or `postgres`) |
| `DB_HOST` | `localhost` | PostgreSQL host |
| `DB_PORT` | `5432` | PostgreSQL port |
| `DB_NAME` | `analytics_demo` | Database name |
| `DB_USER` | `readonly` | Database user |
| `DB_PASSWORD` | *(empty)* | Database password |

### File Handling

| Variable | Default | Description |
|----------|---------|-------------|
| `UPLOAD_DIR` | `/tmp/nas_uploads` | Temporary upload directory |
| `MAX_FILE_MB` | `50` | Maximum upload size in MB |

### RAG Tuning

| Variable | Default | Description |
|----------|---------|-------------|
| `CHUNK_SIZE` | `500` | Words per document chunk |
| `CHUNK_OVERLAP` | `50` | Overlap between consecutive chunks |
| `TOP_K` | `4` | Number of chunks retrieved per query |

### Session

| Variable | Default | Description |
|----------|---------|-------------|
| `SESSION_TTL` | `7200` | Session time-to-live in seconds (2 hours) |

---

### Usage

Import individual constants anywhere in the project:

```python
from utils.config import OLLAMA_BASE_URL, OLLAMA_CHAT_MODEL, VECTOR_DIMS

print(OLLAMA_BASE_URL)   # http://localhost:11434
print(VECTOR_DIMS)       # 384
```

Override any value at runtime via environment variable:

```bash
# Override model for a session
OLLAMA_CHAT_MODEL=mistral:7b streamlit run app.py

# Point to a remote Ollama instance
OLLAMA_BASE_URL=http://10.0.1.47:11434 streamlit run app.py
```

Or set them in a `.env` file and load with `python-dotenv`:

```bash
pip install python-dotenv
```

```python
# At the top of app.py
from dotenv import load_dotenv
load_dotenv()
```
