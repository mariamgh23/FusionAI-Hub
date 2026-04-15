# 🤖 AI Platform

A modular, local-first AI assistant platform powered by [Ollama](https://ollama.com). Six independent AI capabilities — RAG, task automation, voice, document intelligence, analytics, and security — unified under a single Streamlit interface.

## 🏷️ Tech Stack

![Streamlit](https://img.shields.io/badge/Streamlit-Web_UI-red)
![Requests](https://img.shields.io/badge/Requests-API_Client-blue)
![Pandas](https://img.shields.io/badge/Pandas-Data_Analytics-lightgrey)
![PyPDF](https://img.shields.io/badge/PyPDF-PDF_Processing-orange)
![Python-Docx](https://img.shields.io/badge/python--docx-DOCX_Processing-green)
![Faster-Whisper](https://img.shields.io/badge/Faster--Whisper-Speech_to_Text-purple)
![SoundDevice](https://img.shields.io/badge/SoundDevice-Audio_Input-yellow)
![SoundFile](https://img.shields.io/badge/SoundFile-Audio_Processing-yellowgreen)
![pyttsx3](https://img.shields.io/badge/pyttsx3-Offline_TTS-blueviolet)
![gTTS](https://img.shields.io/badge/gTTS-Online_TTS-success)
![Google API](https://img.shields.io/badge/Google_API-Gmail_Integration-red)

> **No cloud API keys required.** Everything runs on your machine using open-source models.

---

## ✨ Features

| Module | Description |
|--------|-------------|
| 🔍 **RAG Assistant** | Upload documents, build a local knowledge base, and get cited answers |
| 🤖 **Task Agent** | Decompose goals into steps and execute them — including sending emails |
| 🎙️ **Voice Assistant** | Speak to the AI and hear it respond (fully offline) |
| 📄 **Document Intelligence** | Summarize, Q&A, and extract entities from PDF / DOCX / TXT files |
| 📊 **Analytics AI** | Ask plain-English questions about your database and get SQL + insights |
| 🛡️ **Security AI** | Analyze logs, classify threats, and generate incident reports |

---

## 📁 Repository Structure

```
.
├── app.py                   # Main Streamlit application entry point
├── requirements.txt         # Python dependencies
├── generate_test_data.py    # Script to create sample data files
│
├── modules/                 # Feature modules (one per capability)
│   ├── rag.py               # Retrieval-Augmented Generation
│   ├── task.py              # Task Agent + Gmail integration
│   ├── voice.py             # Speech-to-text, TTS, mic recording
│   ├── docint.py            # Document Intelligence
│   ├── analytics.py         # Natural language → SQL → insights
│   ├── security.py          # Log analysis and threat classification
│   └── gmail.py             # Gmail OAuth2 helper (used by task.py)
│
├── utils/                   # Shared utilities
│   ├── llm.py               # Ollama client (chat, embed, health check)
│   └── config.py            # Environment-based configuration registry
│
└── test_data/               # Sample files for trying each feature
    ├── knowledge_base.txt
    ├── business_report.txt
    ├── service_contract.txt
    ├── analytics_test.db
    ├── security_logs.txt
    ├── security_logs.json
    └── voice_transcript_sample.txt
```

---

## 🚀 Quick Start

### 1. Prerequisites

- Python 3.10+
- [Ollama](https://ollama.com) installed and running

### 2. Pull required models

```bash
ollama pull llama3.1:8b
ollama pull nomic-embed-text
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the app

```bash
# Terminal 1 — start Ollama (if not already running)
ollama serve

# Terminal 2 — start the app
streamlit run app.py
```

Open your browser at **http://localhost:8501**

### 5. Generate sample data (optional)

```bash
python generate_test_data.py
```

This creates ready-to-use files in `test_data/` for every module.

---

## ⚙️ Configuration

All settings are controlled via environment variables. Copy and edit as needed:

```bash
# LLM
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_CHAT_MODEL=llama3.1:8b
OLLAMA_EMBED_MODEL=nomic-embed-text

# Vector / Search (for cloud deployment)
ES_HOST=http://localhost:9200
ES_USERNAME=admin
ES_PASSWORD=admin
ES_RAG_INDEX=knowledge
VECTOR_DIMS=384

# Database (Analytics AI)
DB_TYPE=sqlite                  # or "postgres"
DB_HOST=localhost
DB_PORT=5432
DB_NAME=analytics_demo
DB_USER=readonly
DB_PASSWORD=

# File uploads
UPLOAD_DIR=/tmp/uploads
MAX_FILE_MB=50
```

See [`utils/config.py`](utils/config.py) for the full list with defaults.

---

## 📦 Dependencies

| Package | Purpose |
|---------|---------|
| `streamlit` | Web UI framework |
| `requests` | Ollama REST API client |
| `pandas` | Data handling (Analytics AI) |
| `pypdf` | PDF text extraction |
| `python-docx` | DOCX text extraction |
| `faster-whisper` | Offline speech-to-text |
| `sounddevice` + `soundfile` | Microphone recording |
| `pyttsx3` | Offline text-to-speech |
| `gtts` | Online TTS fallback |
| `google-api-python-client` | Gmail API (Task Agent) |

Install everything at once:

```bash
pip install -r requirements.txt
```

---

## 🔌 Optional: Gmail Integration

The Task Agent can detect and execute email steps automatically. To enable it:

1. Go to [Google Cloud Console](https://console.cloud.google.com) → APIs & Services → Credentials
2. Create an **OAuth 2.0 Client ID** (Desktop app type)
3. Download the JSON file and save it as `credentials/gmail_oauth.json`
4. On first use, a browser window opens for one-time authorization — the token is cached automatically

See [`modules/gmail.py`](modules/gmail.py) for full setup details.

---

## ☁️ Cloud Deployment

This platform was validated on **Huawei Cloud ME-Riyadh** using:

| Service | Role |
|---------|------|
| GPU ECS (Tesla T4) | Ollama LLM runtime |
| CSS (Elasticsearch) | Vector index (replaces in-memory store) |
| CCE (Kubernetes) | Container orchestration |
| OBS | Document and artifact storage |
| SWR | Container image registry |

See the enterprise blueprint document for the full deployment architecture.

---

## 📚 Module Documentation

Each module has its own README with API reference and usage examples:

- [`modules/README.md`](modules/README.md) — All modules overview
- [`modules/rag.py`](modules/) — RAG Assistant
- [`modules/task.py`](modules/) — Task Agent
- [`modules/voice.py`](modules/) — Voice Assistant
- [`modules/docint.py`](modules/) — Document Intelligence
- [`modules/analytics.py`](modules/) — Analytics AI
- [`modules/security.py`](modules/) — Security AI
- [`utils/README.md`](utils/README.md) — LLM client and config
- [`test_data/README.md`](test_data/README.md) — Sample data guide

---

## 🧱 Architecture Overview

```
┌─────────────────────────────────────────────┐
│              Streamlit UI (app.py)          │
│  Sidebar: RAG │ Task │ Voice │ Doc │ ...    │
└────────┬────────────────────────────────────┘
         │  lazy imports per selected feature
    ┌────▼──────────────────────────────┐
    │           Feature Modules         │
    │  rag  task  voice  docint         │
    │  analytics  security  gmail       │
    └────┬──────────────────────────────┘
         │  shared utils layer
    ┌────▼──────────────────────────────┐
    │           utils/llm.py            │
    │   chat()  embed()  available()    │
    └────┬──────────────────────────────┘
         │  HTTP REST
    ┌────▼──────────────────────────────┐
    │        Ollama (local server)      │
    │   llama3.1:8b  nomic-embed-text   │
    └───────────────────────────────────┘
```

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Commit your changes: `git commit -m 'Add my feature'`
4. Push to the branch: `git push origin feature/my-feature`
5. Open a Pull Request

---

## 📄 License

MIT License — see `LICENSE` for details.
