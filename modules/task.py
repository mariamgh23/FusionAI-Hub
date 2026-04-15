"""Task Agent: break a goal into steps and optionally execute them via LLM.

Gmail actions are detected automatically when a step contains send/email keywords.
All other steps are executed via the LLM as before.
"""
import json
import re
from utils.llm import chat


def plan_tasks(goal: str) -> list[str]:
    system = (
        "You are a task planning assistant. "
        "Given a goal, return a JSON array of concise action steps (strings). "
        "Respond with ONLY valid JSON, no markdown."
    )
    raw = chat(goal, system)
    try:
        steps = json.loads(raw)
        if isinstance(steps, list):
            return [str(s) for s in steps]
    except Exception:
        pass
    return [line.strip("•-– ") for line in raw.splitlines() if line.strip()]


# ── Gmail action detection ────────────────────────────────────────────────────

_EMAIL_PATTERN = re.compile(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}")
_EMAIL_KEYWORDS = re.compile(r"\b(send|email|mail|notify|draft)\b", re.IGNORECASE)


def _is_email_task(task: str) -> bool:
    return bool(_EMAIL_KEYWORDS.search(task) and _EMAIL_PATTERN.search(task))


def _extract_email_fields(task: str) -> tuple[str, str, str]:
    """Ask the LLM to extract to/subject/body from an informal task description."""
    system = (
        "Extract email fields from this task description. "
        "Respond ONLY with a JSON object with keys: to, subject, body. "
        "No markdown, no explanation."
    )
    raw = chat(task, system)
    try:
        raw = raw.strip().strip("```json").strip("```").strip()
        data = json.loads(raw)
        return data.get("to", ""), data.get("subject", "No subject"), data.get("body", task)
    except Exception:
        # Last-resort: parse address from the task string directly
        match = _EMAIL_PATTERN.search(task)
        to = match.group(0) if match else ""
        return to, "Task notification", task


# ── Public API (unchanged signature) ─────────────────────────────────────────

def execute_task(task: str) -> str:
    """Execute a single task step.

    If the step looks like a send-email action and Gmail is configured,
    it sends the email. Otherwise falls back to LLM execution.
    """
    if _is_email_task(task):
        from modules.gmail import send_email, gmail_available
        ok, reason = gmail_available()
        if ok:
            to, subject, body = _extract_email_fields(task)
            if not to:
                return "⚠️ Could not extract a recipient address from the task description."
            try:
                result = send_email(to=to, subject=subject, body=body)
                return f"✅ Email sent to **{to}** (Message ID: `{result.get('id', '?')}`)"
            except Exception as e:
                return f"❌ Gmail send failed: {e}"
        else:
            # Gmail not configured — fall through to LLM simulation
            return (
                f"📧 *(Gmail not configured — {reason})*\n\n"
                + chat(task, "Simulate sending this email and describe what you would send.")
            )

    # Default: LLM execution
    system = (
        "You are an AI agent. Execute the following task and describe what you did "
        "or what the result is. Be concise."
    )
    return chat(task, system)


def send_email_task(to: str, subject: str, body: str) -> str:
    """Directly send an email from the UI form (used by app.py Task Agent tab)."""
    from modules.gmail import send_email, gmail_available
    ok, reason = gmail_available()
    if not ok:
        return f"⚠️ Gmail not configured: {reason}\n\nSetup: place `credentials/gmail_oauth.json` in the project root."
    try:
        result = send_email(to=to, subject=subject, body=body)
        return f"✅ Email sent successfully (Message ID: `{result.get('id', '?')}`)"
    except Exception as e:
        return f"❌ Send failed: {e}"
