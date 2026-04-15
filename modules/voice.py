"""Voice Assistant: mic capture → STT → LLM → TTS.

Speech-to-text: faster-whisper (offline, CPU)
Mic capture:    sounddevice + soundfile
TTS:            pyttsx3 (offline) with gTTS (online) as fallback
"""
from __future__ import annotations
import io
import os
import tempfile
from utils.llm import chat


# ── Speech-to-text ────────────────────────────────────────────────────────────

def transcribe(audio_bytes: bytes, filename: str = "audio.wav") -> str:
    """Transcribe audio bytes using faster-whisper (tiny, CPU)."""
    try:
        from faster_whisper import WhisperModel  # type: ignore
        model = WhisperModel("tiny", device="cpu", compute_type="int8")
        suffix = os.path.splitext(filename)[1] or ".wav"
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as f:
            f.write(audio_bytes)
            tmp_path = f.name
        try:
            segments, _ = model.transcribe(tmp_path)
            return " ".join(s.text for s in segments).strip()
        finally:
            os.unlink(tmp_path)
    except ImportError:
        return (
            "[faster-whisper not installed]\n"
            "Run: pip install faster-whisper\n"
            "Fallback transcript: 'Hello, what can you do?'"
        )
    except Exception as e:
        return f"[Transcription error] {e}"


def record_from_mic(seconds: int = 5, sample_rate: int = 16000) -> bytes:
    """
    Record audio from the default microphone.

    Args:
        seconds:     Recording duration in seconds (default 5).
        sample_rate: Sample rate in Hz (16 kHz matches Whisper's expectation).

    Returns:
        WAV audio as bytes, ready to pass to transcribe().

    Raises:
        RuntimeError if sounddevice or soundfile are not installed.
    """
    try:
        import sounddevice as sd      # type: ignore
        import soundfile as sf        # type: ignore
    except ImportError:
        raise RuntimeError(
            "Mic recording requires sounddevice and soundfile.\n"
            "Run: pip install sounddevice soundfile"
        )

    recording = sd.rec(
        int(seconds * sample_rate),
        samplerate=sample_rate,
        channels=1,
        dtype="int16",
    )
    sd.wait()  # blocks until recording is complete

    buf = io.BytesIO()
    sf.write(buf, recording, sample_rate, format="WAV", subtype="PCM_16")
    return buf.getvalue()


# ── Text-to-speech ────────────────────────────────────────────────────────────

def speak_reply(text: str) -> bytes | None:
    """
    Convert text to speech. Tries pyttsx3 (offline) first, then gTTS (online).
    Returns WAV/MP3 bytes, or None if both are unavailable.
    """
    # ── Option 1: pyttsx3 (fully offline) ────────────────────────────────────
    try:
        import pyttsx3  # type: ignore
        engine = pyttsx3.init()
        # Tune for better clarity
        engine.setProperty("rate", 165)
        engine.setProperty("volume", 1.0)

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            tmp_path = f.name
        engine.save_to_file(text, tmp_path)
        engine.runAndWait()

        with open(tmp_path, "rb") as f:
            data = f.read()
        os.unlink(tmp_path)
        if data:
            return data
    except Exception:
        pass  # fall through to gTTS

    # ── Option 2: gTTS (requires internet) ───────────────────────────────────
    try:
        from gtts import gTTS  # type: ignore
        buf = io.BytesIO()
        gTTS(text=text, lang="en", slow=False).write_to_fp(buf)
        return buf.getvalue()
    except ImportError:
        pass
    except Exception:
        pass

    return None


# ── LLM chat ─────────────────────────────────────────────────────────────────

def voice_chat(transcript: str) -> str:
    system = "You are a friendly voice assistant. Reply in 1–3 short sentences."
    return chat(transcript, system)
