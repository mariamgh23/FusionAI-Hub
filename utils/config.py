import os

OLLAMA_BASE_URL   = os.getenv("OLLAMA_BASE_URL",   "http://localhost:11434")
OLLAMA_CHAT_MODEL = os.getenv("OLLAMA_CHAT_MODEL", "llama3.1:8b")
OLLAMA_EMBED_MODEL= os.getenv("OLLAMA_EMBED_MODEL","nomic-embed-text")

ES_HOST           = os.getenv("ES_HOST",           "http://localhost:9200")
ES_USERNAME       = os.getenv("ES_USERNAME",       "admin")
ES_PASSWORD       = os.getenv("ES_PASSWORD",       "admin")
ES_RAG_INDEX      = os.getenv("ES_RAG_INDEX",      "nas_knowledge")
ES_SECURITY_INDEX = os.getenv("ES_SECURITY_INDEX", "nas_security_logs")
VECTOR_DIMS       = 384

DB_TYPE     = os.getenv("DB_TYPE",     "sqlite")
DB_HOST     = os.getenv("DB_HOST",     "localhost")
DB_PORT     = int(os.getenv("DB_PORT", "5432"))
DB_NAME     = os.getenv("DB_NAME",     "analytics_demo")
DB_USER     = os.getenv("DB_USER",     "readonly")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")

UPLOAD_DIR      = os.getenv("UPLOAD_DIR", "/tmp/nas_uploads")
MAX_FILE_MB     = int(os.getenv("MAX_FILE_MB", "50"))
CHUNK_SIZE      = 500
CHUNK_OVERLAP   = 50
TOP_K           = 4
SESSION_TTL     = int(os.getenv("SESSION_TTL_SECONDS", "7200"))
