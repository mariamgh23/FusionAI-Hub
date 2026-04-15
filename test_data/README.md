# 🗂️ test_data/

Sample files for testing and demonstrating every feature in the platform. Generate them fresh at any time by running:

```bash
python generate_test_data.py
```

---

## Files

| File | Module | Description |
|------|--------|-------------|
| `knowledge_base.txt` | RAG Assistant | Platform technical overview — good for Q&A demos |
| `business_report.txt` | Document Intelligence | Q1 financial report with named people and figures |
| `service_contract.txt` | Document Intelligence | Service agreement with payment schedule and dates |
| `analytics_test.db` | Analytics AI | SQLite database with four realistic tables |
| `security_logs.txt` | Security AI | 17 log events covering brute-force, escalation, malware |
| `security_logs.json` | Security AI | Same events in JSON format for programmatic use |
| `voice_transcript_sample.txt` | Voice Assistant | Sample transcript to paste into the text input |

---

## How to Use Each File

### 🔍 RAG Assistant — `knowledge_base.txt`

1. Open **RAG Assistant** in the sidebar
2. Upload `knowledge_base.txt` using the file uploader
3. Click **Ingest Document** — wait for the chunk count to appear
4. Ask questions in the text field below

**Try these questions:**
```
What models does the platform use?
How does the Voice Assistant work?
What is the chunking strategy?
How is the RAG context assembled?
What formats does Document Intelligence support?
```

---

### 📄 Document Intelligence — `business_report.txt` and `service_contract.txt`

1. Open **Document Intelligence** in the sidebar
2. Upload either file
3. Choose a tab: **Summarize**, **Q&A**, or **Entities**

**Questions for `business_report.txt`:**
```
Who is the CFO?
Which region had the highest sales?
What is the Q2 guidance?
What was the net profit margin?
Who is the VP of Engineering?
```

**Questions for `service_contract.txt`:**
```
What is the payment schedule?
What is the total contract value?
When is the final delivery date?
How long does the confidentiality clause last?
Who signed the agreement?
```

---

### 📊 Analytics AI — `analytics_test.db`

The demo database (auto-created at `~/.ai_platform/demo_analytics.db`) contains four tables:

#### `sales`
```
id, product, region, amount, units, date, rep
```
100 randomized rows across 5 products, 4 regions, and 5 sales reps.

#### `users`
```
id, name, email, region, plan, signup_date, active
```
10 users with free / pro / enterprise plans.

#### `products`
```
id, name, category, price, stock
```
5 products with Hardware / Software categories.

#### `support_tickets`
```
id, user_id, subject, status, priority, created_date
```
50 tickets with open / in_progress / resolved / closed statuses and low–critical priorities.

**Try these questions:**
```
Total sales by region
Top 3 products by revenue
How many open support tickets are critical?
Which sales rep sold the most?
Average order value by product
How many users are on the pro plan?
Which products are low on stock?
Monthly revenue trend
```

---

### 🛡️ Security AI — `security_logs.txt`

The log file contains 17 events across two days covering six threat scenarios:

| Scenario | Events |
|----------|--------|
| Brute-force + account lockout | 7 failed logins → lockout |
| Normal activity | Successful logins, file upload, backup |
| Privilege escalation | `chmod 777 /etc/passwd` → root escalation |
| Data exfiltration | 52 MB outbound to suspicious IP + DLP alert |
| Port scan | 6 ports probed → firewall block |
| Malware detection | Signature match + process termination |

**How to use:**
1. Open **Security AI** in the sidebar
2. **Log Analyzer tab** — paste the contents of `security_logs.txt`
3. **Threat Classifier tab** — try these single-event descriptions:
   ```
   User executed chmod 777 on /etc/passwd after logging in at 2am
   15 failed SSH logins in 30 seconds from 192.168.1.45
   52MB outbound transfer to 185.220.101.3 at midnight
   Process beacon.sh matched malware signature hash a3f2c1d9
   ```
4. **Report Generator tab** — paste the full log for a formatted incident report

---

### 🎙️ Voice Assistant — `voice_transcript_sample.txt`

Content of the file:
```
Hello, I need help setting up the analytics dashboard.
Can you show me how to query the sales data by region?
Also, what is the total revenue for Q1 2024?
```

**How to use:**
1. Open **Voice Assistant** in the sidebar
2. Paste the text into the **"Or type your message directly"** field
3. Click **Get Reply** to hear and see the AI response

Alternatively, use the microphone button or upload an audio file for real speech-to-text testing.

---

## Regenerating Test Data

The `generate_test_data.py` script rebuilds all files with a fixed random seed (`seed=42`) for reproducibility:

```bash
python generate_test_data.py
```

Output:
```
🔧 Generating test data in ./test_data/

  ✅ test_data/knowledge_base.txt
  ✅ test_data/business_report.txt
  ✅ test_data/service_contract.txt
  ✅ test_data/analytics_test.db  (sales, users, products, support_tickets)
  ✅ test_data/security_logs.txt  (17 events)
  ✅ test_data/security_logs.json
  ✅ test_data/voice_transcript_sample.txt

✅ Done!
```
