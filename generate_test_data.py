"""
generate_test_data.py
Run: python generate_test_data.py
Creates a ./test_data/ folder with sample files ready to use in the app.
"""

import os
import sqlite3
import json
import random
from datetime import datetime, timedelta

OUT = "test_data"
os.makedirs(OUT, exist_ok=True)


# ── 1. RAG / plain-text knowledge base ──────────────────────────────────────
def make_txt():
    content = """
NAS AI Platform — Technical Overview
=====================================

The NAS AI Platform is a unified AI system built for network-attached storage environments.
It provides six core capabilities: retrieval-augmented generation, task automation,
voice interaction, document intelligence, analytics, and security monitoring.

Architecture
------------
The platform runs entirely on-premises using Ollama as the local LLM runtime.
The default chat model is llama3.1:8b. Embeddings are generated using nomic-embed-text
which produces 384-dimensional vectors suitable for semantic search.

All configuration is managed through environment variables defined in utils/config.py.
Services share a common LLM utility layer (utils/llm.py) that wraps Ollama's REST API.

RAG Assistant
-------------
Documents are split into 500-token chunks with 50-token overlap.
Chunks are embedded and stored in an in-memory vector store.
At query time, cosine similarity is used to retrieve the top-4 most relevant chunks.
The retrieved context is passed to the LLM with a strict grounding prompt.

Task Agent
----------
The task agent accepts a high-level goal and uses the LLM to decompose it into
actionable steps returned as a JSON array. Each step can then be individually executed.
This is useful for project planning, research workflows, and automation pipelines.

Voice Assistant
---------------
Audio input is transcribed using faster-whisper (tiny model, CPU-optimised).
The transcript is passed to the LLM for a conversational reply.
Optional TTS output is available via pyttsx3 for fully offline voice interaction.

Document Intelligence
---------------------
Supported formats: TXT, PDF, DOCX.
Features include multi-style summarisation (brief, detailed, bullet-points),
open-ended Q&A grounded in document content, and named entity extraction.

Analytics AI
------------
Users ask questions in plain English. The LLM converts them to SQLite-compatible SQL.
Results are returned as a Pandas DataFrame, visualised as a bar chart, and explained
in plain language. A demo database with sales and user tables is auto-created.

Security AI
-----------
Log lines are analysed for threats. Individual events can be classified by type and
severity (Critical / High / Medium / Low). A full incident report can be generated
from any log dump in plain text format.

Deployment
----------
Requirements: Python 3.10+, Ollama, and the packages in requirements.txt.
Start the app with: python -m streamlit run app.py
Ollama must be running separately: ollama serve
""".strip()

    path = f"{OUT}/knowledge_base.txt"
    with open(path, "w") as f:
        f.write(content)
    print(f"  ✅ {path}")


# ── 2. Document Intelligence samples ────────────────────────────────────────
def make_docs():
    report = """
Q1 2024 Business Report — Acme Corporation
===========================================

Executive Summary
-----------------
Acme Corporation achieved record revenue of $4.2M in Q1 2024, representing a 18%
year-over-year increase. The North region led all territories with $1.8M in sales.
Operating expenses rose by 6% due to new hires in the engineering division.

Key People
----------
- CEO: Sarah Mitchell
- CFO: James Okafor
- VP Engineering: Li Wei
- VP Sales: Priya Nair

Financial Highlights
--------------------
Total Revenue:       $4,200,000
Operating Expenses:  $2,100,000
Net Profit:          $2,100,000
Profit Margin:       50%

Regional Breakdown
------------------
North:   $1,800,000  (43%)
South:   $950,000    (23%)
East:    $850,000    (20%)
West:    $600,000    (14%)

Top Products
------------
1. Gadget X    — $1,950,000
2. Widget A    — $1,400,000
3. Widget B    — $850,000

Outlook
-------
Q2 2024 guidance is set at $4.5M–$4.8M. The company plans to launch two new product
lines and expand operations into the European market by June 2024.

Contact
-------
Acme Corporation HQ, 100 Innovation Drive, San Francisco, CA 94107
investor.relations@acme.example.com
""".strip()

    contract = """
SERVICE AGREEMENT
=================
Date: March 1, 2024
Parties: TechVentures LLC ("Client") and NovaSoft Inc. ("Provider")

1. SCOPE OF SERVICES
   Provider agrees to deliver a custom AI integration platform including:
   - REST API development
   - Model fine-tuning services
   - 12 months of technical support

2. PAYMENT TERMS
   Total contract value: $85,000
   Payment schedule:
   - 30% upon signing: $25,500
   - 40% at milestone delivery: $34,000
   - 30% upon completion: $25,500

3. TIMELINE
   Project start: April 1, 2024
   Milestone delivery: July 1, 2024
   Final delivery: October 1, 2024

4. CONFIDENTIALITY
   Both parties agree to keep all project details confidential for 3 years.

5. GOVERNING LAW
   This agreement is governed by the laws of the State of California.

Signed:
_______________________        _______________________
Sarah Mitchell, CEO            David Park, CTO
TechVentures LLC               NovaSoft Inc.
""".strip()

    for name, content in [("business_report.txt", report), ("service_contract.txt", contract)]:
        path = f"{OUT}/{name}"
        with open(path, "w") as f:
            f.write(content)
        print(f"  ✅ {path}")


# ── 3. Analytics database ────────────────────────────────────────────────────
def make_db():
    path = f"{OUT}/analytics_test.db"
    conn = sqlite3.connect(path)

    conn.executescript("""
        DROP TABLE IF EXISTS sales;
        DROP TABLE IF EXISTS users;
        DROP TABLE IF EXISTS products;
        DROP TABLE IF EXISTS support_tickets;
    """)

    # Sales
    conn.execute("""
        CREATE TABLE sales (
            id INTEGER PRIMARY KEY,
            product TEXT,
            region TEXT,
            amount REAL,
            units INTEGER,
            date TEXT,
            rep TEXT
        )
    """)
    products = ["Gadget X", "Widget A", "Widget B", "Pro Suite", "Starter Pack"]
    regions  = ["North", "South", "East", "West"]
    reps     = ["Alice", "Bob", "Carol", "Dave", "Eve"]
    rows = []
    base = datetime(2024, 1, 1)
    for i in range(1, 101):
        p = random.choice(products)
        price = {"Gadget X": 230, "Widget A": 150, "Widget B": 85,
                 "Pro Suite": 400, "Starter Pack": 50}[p]
        units = random.randint(1, 20)
        date  = (base + timedelta(days=random.randint(0, 180))).strftime("%Y-%m-%d")
        rows.append((i, p, random.choice(regions), round(price * units, 2),
                     units, date, random.choice(reps)))
    conn.executemany("INSERT INTO sales VALUES (?,?,?,?,?,?,?)", rows)

    # Users
    conn.execute("""
        CREATE TABLE users (
            id INTEGER PRIMARY KEY,
            name TEXT,
            email TEXT,
            region TEXT,
            plan TEXT,
            signup_date TEXT,
            active INTEGER
        )
    """)
    names = ["Alice Johnson","Bob Smith","Carol White","Dave Brown","Eve Davis",
             "Frank Miller","Grace Lee","Henry Wilson","Irene Moore","Jack Taylor"]
    plans = ["free", "pro", "enterprise"]
    user_rows = []
    for i, name in enumerate(names, 1):
        first = name.split()[0].lower()
        date  = (base + timedelta(days=random.randint(-365, 0))).strftime("%Y-%m-%d")
        user_rows.append((i, name, f"{first}@example.com", random.choice(regions),
                          random.choice(plans), date, random.randint(0, 1)))
    conn.executemany("INSERT INTO users VALUES (?,?,?,?,?,?,?)", user_rows)

    # Products
    conn.execute("""
        CREATE TABLE products (
            id INTEGER PRIMARY KEY,
            name TEXT,
            category TEXT,
            price REAL,
            stock INTEGER
        )
    """)
    conn.executemany("INSERT INTO products VALUES (?,?,?,?,?)", [
        (1, "Gadget X",     "Hardware", 230.0, 145),
        (2, "Widget A",     "Hardware", 150.0, 320),
        (3, "Widget B",     "Hardware",  85.0, 512),
        (4, "Pro Suite",    "Software", 400.0, 999),
        (5, "Starter Pack", "Software",  50.0, 999),
    ])

    # Support tickets
    conn.execute("""
        CREATE TABLE support_tickets (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            subject TEXT,
            status TEXT,
            priority TEXT,
            created_date TEXT
        )
    """)
    subjects  = ["Login issue", "Billing question", "Feature request",
                 "Bug report", "Performance problem", "Setup help"]
    statuses  = ["open", "in_progress", "resolved", "closed"]
    priorities= ["low", "medium", "high", "critical"]
    ticket_rows = []
    for i in range(1, 51):
        date = (base + timedelta(days=random.randint(0, 180))).strftime("%Y-%m-%d")
        ticket_rows.append((i, random.randint(1, 10), random.choice(subjects),
                            random.choice(statuses), random.choice(priorities), date))
    conn.executemany("INSERT INTO support_tickets VALUES (?,?,?,?,?,?)", ticket_rows)

    conn.commit()
    conn.close()
    print(f"  ✅ {path}  (sales, users, products, support_tickets)")


# ── 4. Security logs ─────────────────────────────────────────────────────────
def make_logs():
    base = datetime(2024, 3, 1, 0, 0, 0)

    events = [
        # Brute-force
        *[(base + timedelta(seconds=i*2), "WARN",
           f"Failed login attempt user=root ip=192.168.1.45 attempt={i}")
          for i in range(1, 8)],
        (base + timedelta(seconds=16), "ERROR",
         "Account locked user=root ip=192.168.1.45 after=7 failures"),

        # Normal activity
        (base + timedelta(hours=8),      "INFO",  "User admin logged in ip=10.0.0.5"),
        (base + timedelta(hours=8, minutes=30), "INFO",
         "File uploaded filename=q1_report.pdf user=admin size=2.1MB"),
        (base + timedelta(hours=9),      "INFO",  "User jdoe logged in ip=10.0.0.12"),
        (base + timedelta(hours=9, minutes=15), "INFO",
         "Database backup completed size=512MB duration=45s"),

        # Privilege escalation
        (base + timedelta(hours=11),     "WARN",
         "Sudo command executed user=jdoe cmd='chmod 777 /etc/passwd'"),
        (base + timedelta(hours=11, minutes=1), "ERROR",
         "Privilege escalation detected user=jdoe escalated_to=root"),

        # Data exfiltration
        (base + timedelta(hours=23, minutes=58), "WARN",
         "Unusual outbound traffic volume=52MB dest=185.220.101.3 port=443"),
        (base + timedelta(hours=23, minutes=59), "ERROR",
         "DLP alert: sensitive data pattern detected in outbound stream dest=185.220.101.3"),

        # Port scan
        (base + timedelta(days=1, minutes=1), "ERROR",
         "Port scan detected src=203.0.113.77 ports=22,80,443,3306,8080,8443"),
        (base + timedelta(days=1, minutes=2), "WARN",
         "Firewall rule triggered src=203.0.113.77 action=block"),

        # Malware
        (base + timedelta(days=1, hours=3), "CRITICAL",
         "Malware signature matched file=/tmp/.hidden/beacon.sh hash=a3f2c1d9"),
        (base + timedelta(days=1, hours=3, minutes=1), "CRITICAL",
         "Process terminated pid=4821 name=beacon.sh reason=malware"),

        # Normal close
        (base + timedelta(days=1, hours=17), "INFO",  "User admin logged out session_duration=8h32m"),
        (base + timedelta(days=1, hours=23), "INFO",  "Nightly vulnerability scan completed findings=3"),
    ]

    lines = [f"{ts.strftime('%Y-%m-%d %H:%M:%S')} {level:<8} {msg}"
             for ts, level, msg in events]
    log_text = "\n".join(lines)

    path = f"{OUT}/security_logs.txt"
    with open(path, "w") as f:
        f.write(log_text)
    print(f"  ✅ {path}  ({len(lines)} events)")

    # Also save as JSON for programmatic use
    json_path = f"{OUT}/security_logs.json"
    with open(json_path, "w") as f:
        json.dump([{"timestamp": ts.isoformat(), "level": level, "message": msg}
                   for ts, level, msg in events], f, indent=2)
    print(f"  ✅ {json_path}")


# ── 5. Voice transcript sample ───────────────────────────────────────────────
def make_voice_sample():
    content = (
        "Hello, I need help setting up the analytics dashboard. "
        "Can you show me how to query the sales data by region? "
        "Also, what is the total revenue for Q1 2024?"
    )
    path = f"{OUT}/voice_transcript_sample.txt"
    with open(path, "w") as f:
        f.write(content)
    print(f"  ✅ {path}  (paste into Voice Assistant text input)")


# ── 6. README ────────────────────────────────────────────────────────────────
def make_readme():
    readme = """
# Test Data — NAS AI Platform

## Files

| File | Feature | How to use |
|------|---------|------------|
| `knowledge_base.txt` | RAG Assistant | Upload → Ingest, then ask questions |
| `business_report.txt` | Document Intelligence | Upload → Summarize / Q&A / Entities |
| `service_contract.txt` | Document Intelligence | Upload → Q&A (try: "What is the payment schedule?") |
| `analytics_test.db` | Analytics AI | Copy path into app DB field (or set DB_PATH env var) |
| `security_logs.txt` | Security AI | Paste contents into Log Analyzer tab |
| `security_logs.json` | Security AI | Programmatic use / import |
| `voice_transcript_sample.txt` | Voice Assistant | Paste text into the direct-input field |

## Sample Questions to Try

### RAG Assistant
- "What models does the platform use?"
- "How does the Voice Assistant work?"
- "What is the chunking strategy?"

### Document Intelligence (business_report.txt)
- "Who is the CFO?"
- "Which region had the highest sales?"
- "What is the Q2 guidance?"

### Analytics AI
- "Total sales by region"
- "Top 3 products by revenue"
- "How many open support tickets are critical?"
- "Which sales rep sold the most?"

### Security AI
- Paste `security_logs.txt` contents into the Log Analyzer
- Classify event: "User executed chmod 777 on /etc/passwd after logging in at 2am"
""".strip()

    path = f"{OUT}/README.md"
    with open(path, "w") as f:
        f.write(readme)
    print(f"  ✅ {path}")


# ── Main ─────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    random.seed(42)
    print(f"\n🔧 Generating test data in ./{OUT}/\n")
    make_txt()
    make_docs()
    make_db()
    make_logs()
    make_voice_sample()
    make_readme()
    print(f"\n✅ Done! Open ./{OUT}/README.md for usage instructions.\n")
