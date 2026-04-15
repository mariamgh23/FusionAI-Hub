"""Document Intelligence: extract, summarize, and Q&A over uploaded documents."""
from __future__ import annotations
import io
from utils.llm import chat


def extract_text(file_bytes: bytes, filename: str) -> str:
    ext = filename.rsplit(".", 1)[-1].lower()
    if ext == "txt":
        return file_bytes.decode("utf-8", errors="ignore")
    elif ext == "pdf":
        try:
            import pypdf  # type: ignore
            reader = pypdf.PdfReader(io.BytesIO(file_bytes))
            return "\n".join(p.extract_text() or "" for p in reader.pages)
        except ImportError:
            return "[pypdf not installed — install with: pip install pypdf]"
        except Exception as e:
            return f"[PDF read error] {e}"
    elif ext in ("docx",):
        try:
            import docx  # type: ignore
            doc = docx.Document(io.BytesIO(file_bytes))
            return "\n".join(p.text for p in doc.paragraphs)
        except ImportError:
            return "[python-docx not installed — install with: pip install python-docx]"
        except Exception as e:
            return f"[DOCX read error] {e}"
    else:
        try:
            return file_bytes.decode("utf-8", errors="ignore")
        except Exception:
            return "[Unsupported file type]"


def summarize(text: str, style: str = "brief") -> str:
    style_map = {
        "brief":    "Summarize this document in 3–5 sentences.",
        "detailed": "Provide a detailed summary with key points and takeaways.",
        "bullets":  "Summarize this document as a bullet-point list of key facts.",
    }
    system  = style_map.get(style, style_map["brief"])
    prompt  = f"Document:\n\n{text[:4000]}"
    return chat(prompt, system)


def answer_question(text: str, question: str) -> str:
    system = "Answer the question using only the document content provided. Be concise."
    prompt = f"Document:\n\n{text[:4000]}\n\nQuestion: {question}"
    return chat(prompt, system)


def extract_entities(text: str) -> str:
    system = (
        "Extract named entities from this document. "
        "Group them by type: People, Organizations, Dates, Locations, Key Terms. "
        "Format as a clean list."
    )
    return chat(f"Document:\n\n{text[:4000]}", system)
