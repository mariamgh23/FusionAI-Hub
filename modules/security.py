"""Security AI: analyze log lines / events and classify threats."""
from __future__ import annotations
import json
from utils.llm import chat

SAMPLE_LOGS = """\
2024-03-01 02:14:33 WARN  Failed login attempt user=root ip=192.168.1.45
2024-03-01 02:14:35 WARN  Failed login attempt user=root ip=192.168.1.45
2024-03-01 02:14:37 WARN  Failed login attempt user=root ip=192.168.1.45
2024-03-01 02:14:39 ERROR Locked out user=root after 5 failures ip=192.168.1.45
2024-03-01 08:00:01 INFO  User admin logged in ip=10.0.0.5
2024-03-01 08:45:22 INFO  File uploaded filename=report.pdf user=admin
2024-03-01 23:58:11 WARN  Unusual outbound traffic volume=52MB dest=185.220.101.3
2024-03-02 00:01:44 ERROR Port scan detected src=203.0.113.77 ports=22,80,443,8080
"""


def analyze_logs(log_text: str) -> str:
    system = (
        "You are a cybersecurity analyst. Analyze the provided logs and:\n"
        "1. Identify any security threats or anomalies.\n"
        "2. Classify each finding by severity (Critical/High/Medium/Low).\n"
        "3. Suggest immediate remediation steps.\n"
        "Format your response with clear sections."
    )
    return chat(f"Logs:\n\n{log_text[:5000]}", system)


def classify_threat(event: str) -> dict:
    system = (
        "Classify this security event. Respond ONLY with a JSON object with keys: "
        "threat_type, severity (Critical/High/Medium/Low/Info), confidence (0-100), description."
        " No markdown."
    )
    raw = chat(event, system)
    try:
        return json.loads(raw)
    except Exception:
        return {"threat_type": "Unknown", "severity": "Unknown", "confidence": 0, "description": raw}


def generate_report(log_text: str) -> str:
    system = (
        "Generate a professional security incident report from these logs. "
        "Include: Executive Summary, Findings, Risk Assessment, Recommendations. "
        "Use clear headings."
    )
    return chat(f"Logs:\n\n{log_text[:5000]}", system)
