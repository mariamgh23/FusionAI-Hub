"""
Gmail integration for the Task Agent.
Uses OAuth2 via google-auth + googleapiclient.

Setup (one-time):
  1. Go to https://console.cloud.google.com → APIs & Services → Credentials
  2. Create an OAuth 2.0 Client ID (Desktop app)
  3. Download the JSON and save as credentials/gmail_oauth.json
  4. On first run, a browser window opens to authorise — token is cached in
     credentials/gmail_token.json automatically.

Install dependencies:
  pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
"""
from __future__ import annotations
import base64
import os
import pathlib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Paths — never hard-code secrets in source
_CREDS_DIR   = pathlib.Path(os.getenv("GMAIL_CREDS_DIR", "credentials"))
_OAUTH_FILE  = _CREDS_DIR / "gmail_oauth.json"    # downloaded from Google Cloud
_TOKEN_FILE  = _CREDS_DIR / "gmail_token.json"    # auto-created after first auth
_SCOPES      = ["https://www.googleapis.com/auth/gmail.send"]


def _get_service():
    """Return an authorised Gmail API service object."""
    try:
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
        from google.auth.transport.requests import Request
        from googleapiclient.discovery import build
    except ImportError as e:
        raise RuntimeError(
            "Gmail dependencies missing. "
            "Run: pip install google-auth google-auth-oauthlib "
            "google-auth-httplib2 google-api-python-client"
        ) from e

    creds = None

    if _TOKEN_FILE.exists():
        creds = Credentials.from_authorized_user_file(str(_TOKEN_FILE), _SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not _OAUTH_FILE.exists():
                raise FileNotFoundError(
                    f"Gmail OAuth credentials not found at {_OAUTH_FILE}.\n"
                    "Download your OAuth2 JSON from Google Cloud Console and place it there."
                )
            flow = InstalledAppFlow.from_client_secrets_file(str(_OAUTH_FILE), _SCOPES)
            creds = flow.run_local_server(port=0)

        _CREDS_DIR.mkdir(parents=True, exist_ok=True)
        _TOKEN_FILE.write_text(creds.to_json())

    return build("gmail", "v1", credentials=creds)


def send_email(to: str, subject: str, body: str, html: bool = False) -> dict:
    """
    Send an email via the authenticated Gmail account.

    Args:
        to:      Recipient address (e.g. "alice@example.com")
        subject: Email subject line
        body:    Plain-text or HTML body
        html:    If True, body is treated as HTML

    Returns:
        Gmail API response dict on success.

    Raises:
        RuntimeError if credentials are missing or send fails.
    """
    service = _get_service()

    mime_type = "html" if html else "plain"
    msg = MIMEMultipart("alternative")
    msg["To"]      = to
    msg["Subject"] = subject
    msg.attach(MIMEText(body, mime_type))

    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
    result = service.users().messages().send(
        userId="me", body={"raw": raw}
    ).execute()
    return result


def gmail_available() -> tuple[bool, str]:
    """
    Check whether Gmail integration is configured.
    Returns (True, "") or (False, reason_string).
    """
    try:
        from google.oauth2.credentials import Credentials          # noqa: F401
        from googleapiclient.discovery import build                # noqa: F401
    except ImportError:
        return False, "google-api-python-client not installed"

    if not _OAUTH_FILE.exists() and not _TOKEN_FILE.exists():
        return False, f"OAuth file missing: {_OAUTH_FILE}"

    return True, ""
