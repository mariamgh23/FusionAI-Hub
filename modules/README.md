# 📦 modules/

This directory contains the six feature modules that power the AI platform. Each module is self-contained and communicates with the shared LLM layer in `utils/`.

---

## Module Index

| File | Feature | Key Functions |
|------|---------|---------------|
| [`rag.py`](#-ragpy--rag-assistant) | RAG Assistant | `ingest()`, `run_rag()`, `retrieve()` |
| [`task.py`](#-taskpy--task-agent) | Task Agent | `plan_tasks()`, `execute_task()`, `send_email_task()` |
| [`voice.py`](#-voicepy--voice-assistant) | Voice Assistant | `transcribe()`, `voice_chat()`, `speak_reply()`, `record_from_mic()` |
| [`docint.py`](#-docintpy--document-intelligence) | Document Intelligence | `extract_text()`, `summarize()`, `answer_question()`, `extract_entities()` |
| [`analytics.py`](#-analyticspy--analytics-ai) | Analytics AI | `nl_to_sql()`, `run_query()`, `explain_results()`, `create_demo_db()` |
| [`security.py`](#-securitypy--security-ai) | Security AI | `analyze_logs()`, `classify_threat()`, `generate_report()` |
| [`gmail.py`](#-gmailpy--gmail-integration) | Gmail Integration | `send_email()`, `gmail_available()` |

---

## 🔍 rag.py — RAG Assistant

Implements a complete Retrieval-Augmented Generation pipeline entirely in-process.

### How it works

1. Documents are split into 500-word chunks
2. Each chunk is embedded via `nomic-embed-text` (384-dim vectors)
3. Chunks and vectors are stored in an in-memory list
4. At query time, cosine similarity ranks all chunks against the query vector
5. The top-4 chunks are assembled into a grounded context prompt for the LLM

### Functions

```python
ingest(text: str, chunk_size: int = 500) -> int
```
Splits `text` into chunks, embeds each, and appends to the in-memory store.
Returns the number of chunks ingested.

```python
retrieve(query: str, top_k: int = 4) -> list[str]
```
Embeds `query` and returns the top-`k` most similar chunk texts.

```python
run_rag(query: str) -> str
```
Retrieves context via `retrieve()` and generates a grounded LLM answer.
Returns a warning string if no documents have been ingested yet.

```python
clear_store()
```
Empties the in-memory vector store.

```python
store_size() -> int
```
Returns the number of chunks currently in the store.

### Notes

- The vector store resets when the Python process restarts (in-memory only)
- For persistent storage, swap the `_store` list for an Elasticsearch / CSS index
- Embedding dimension is 384 — must match `VECTOR_DIMS` in config if using an external index

---

## 🤖 task.py — Task Agent

Decomposes high-level goals into executable steps using the LLM, and can automatically route email steps to the Gmail API.

### Functions

```python
plan_tasks(goal: str) -> list[str]
```
Sends `goal` to the LLM with a JSON-array system prompt.
Returns a list of action step strings.

```python
execute_task(task: str) -> str
```
Executes a single task step. If the step matches the email pattern (contains a send/email/mail/notify/draft keyword **and** a valid email address), it attempts to send via Gmail. Otherwise, the LLM simulates execution.

```python
send_email_task(to: str, subject: str, body: str) -> str
```
Directly sends an email from the UI compose form. Used by `app.py`.

### Email detection logic

```python
# Step is routed to Gmail when BOTH conditions are true:
_EMAIL_KEYWORDS = re.compile(r"\b(send|email|mail|notify|draft)\b", re.IGNORECASE)
_EMAIL_PATTERN  = re.compile(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}")
```

If Gmail is not configured, the step falls back to LLM simulation with a clear warning.

---

## 🎙️ voice.py — Voice Assistant

Full speech-to-text → LLM → text-to-speech pipeline with microphone support.

### Functions

```python
record_from_mic(seconds: int = 5, sample_rate: int = 16000) -> bytes
```
Records audio from the default system microphone.
Returns WAV bytes. Raises `RuntimeError` if `sounddevice` / `soundfile` are missing.

```python
transcribe(audio_bytes: bytes, filename: str = "audio.wav") -> str
```
Transcribes audio using `faster-whisper` (tiny model, CPU, int8 quantization).
Writes audio to a temp file, transcribes, then cleans up.
Returns a fallback message string if `faster-whisper` is not installed.

```python
voice_chat(transcript: str) -> str
```
Sends the transcript to the LLM with a voice-optimised system prompt (1–3 short sentences).

```python
speak_reply(text: str) -> bytes | None
```
Converts text to speech. Tries `pyttsx3` (offline) first, then `gTTS` (online).
Returns audio bytes, or `None` if neither is available.

### Optional dependencies

| Package | Role | Install |
|---------|------|---------|
| `faster-whisper` | Speech-to-text | `pip install faster-whisper` |
| `sounddevice` | Mic capture | `pip install sounddevice` |
| `soundfile` | WAV encoding | `pip install soundfile` |
| `pyttsx3` | Offline TTS | `pip install pyttsx3` |
| `gtts` | Online TTS fallback | `pip install gtts` |

All are optional — the module degrades gracefully with informative messages if missing.

---

## 📄 docint.py — Document Intelligence

Multi-format document parsing with three analysis modes.

### Functions

```python
extract_text(file_bytes: bytes, filename: str) -> str
```
Extracts plain text from `.txt`, `.pdf`, or `.docx` files.
Falls back to UTF-8 decode for unknown extensions.

```python
summarize(text: str, style: str = "brief") -> str
```
Summarizes document text. `style` options:
- `"brief"` — 3–5 sentences
- `"detailed"` — key points and takeaways
- `"bullets"` — bullet-point list

```python
answer_question(text: str, question: str) -> str
```
Answers `question` using **only** the document content. LLM is instructed not to use outside knowledge.

```python
extract_entities(text: str) -> str
```
Extracts named entities grouped by type: People, Organizations, Dates, Locations, Key Terms.

### Notes

- All functions truncate input to 4,000 characters to fit within LLM context limits
- PDF support requires `pypdf` — `pip install pypdf`
- DOCX support requires `python-docx` — `pip install python-docx`

---

## 📊 analytics.py — Analytics AI

Converts natural language questions to SQL, executes queries, and explains results.

### Functions

```python
nl_to_sql(question: str, schema: str) -> str
```
Sends `question` and `schema` to the LLM. Returns a clean SQL SELECT statement (strips markdown fences automatically).

```python
run_query(db_path: str, sql: str) -> pd.DataFrame
```
Executes `sql` against the SQLite database at `db_path`. Returns a pandas DataFrame.

```python
explain_results(question: str, df: pd.DataFrame) -> str
```
Sends the original question and query results to the LLM for a plain-English explanation.

```python
create_demo_db(db_path: str = "") -> str
```
Creates (or resets) a demo SQLite database at `~/.ai_platform/demo_analytics.db`.
Tables: `sales`, `users`. Returns the path string.

```python
_get_schema(conn: sqlite3.Connection) -> str
```
Internal helper. Returns a compact schema string like `table(col1 TYPE, col2 TYPE, ...)`.

### Demo database schema

```sql
sales(id INTEGER, product TEXT, region TEXT, amount REAL, date TEXT)
users(id INTEGER, name TEXT, region TEXT, signup_date TEXT)
```

### Notes

- For production use, connect to PostgreSQL by setting `DB_TYPE=postgres` and the `DB_*` env vars in `config.py`
- The LLM is instructed to return **only** a SQL SELECT — no DDL or destructive statements

---

## 🛡️ security.py — Security AI

Three security operations functions: log analysis, threat classification, and report generation.

### Constants

```python
SAMPLE_LOGS: str
```
A multi-line string of realistic sample log entries (brute-force, port scan, data exfiltration) used as the default input in the UI.

### Functions

```python
analyze_logs(log_text: str) -> str
```
Analyzes log text and returns a structured report covering:
- Identified threats and anomalies
- Severity classification per finding (Critical / High / Medium / Low)
- Immediate remediation steps

```python
classify_threat(event: str) -> dict
```
Classifies a single security event description. Returns a dictionary:

```python
{
    "threat_type": str,      # e.g. "Brute Force Attack"
    "severity": str,         # "Critical" | "High" | "Medium" | "Low" | "Info"
    "confidence": int,       # 0–100
    "description": str       # human-readable explanation
}
```

Returns a safe fallback dict if the LLM response is not valid JSON.

```python
generate_report(log_text: str) -> str
```
Generates a professional security incident report with four sections:
- Executive Summary
- Findings
- Risk Assessment
- Recommendations

### Notes

- All functions truncate input to 5,000 characters
- `classify_threat` relies on the LLM returning valid JSON — the fallback handles malformed output gracefully

---

## 📧 gmail.py — Gmail Integration

OAuth2-based Gmail sending helper. Used exclusively by `task.py`.

### Functions

```python
send_email(to: str, subject: str, body: str, html: bool = False) -> dict
```
Sends an email via the authenticated Gmail account.
- `html=True` sends the body as HTML instead of plain text
- Returns the Gmail API response dict on success
- Raises `RuntimeError` on credential or send failure

```python
gmail_available() -> tuple[bool, str]
```
Returns `(True, "")` if Gmail is configured, or `(False, reason)` if not.

### Setup

```
1. Google Cloud Console → APIs & Services → Credentials
2. Create OAuth 2.0 Client ID (Desktop app)
3. Download JSON → save as credentials/gmail_oauth.json
4. First run opens browser for one-time authorization
5. Token cached at credentials/gmail_token.json (auto-refreshed)
```

### Required packages

```bash
pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

### Credential paths

| File | Purpose |
|------|---------|
| `credentials/gmail_oauth.json` | OAuth2 client secrets (from Google Cloud) |
| `credentials/gmail_token.json` | Cached access + refresh token (auto-created) |

Override the credentials directory with the `GMAIL_CREDS_DIR` environment variable.
