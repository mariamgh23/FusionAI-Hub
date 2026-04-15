"""NAS AI Platform — Unified Streamlit App"""
import streamlit as st

st.set_page_config(page_title="NAS AI Platform", page_icon="🤖", layout="wide")

# ── Sidebar navigation ──────────────────────────────────────────────────────
FEATURES = [
    "🔍 RAG Assistant",
    "🤖 Task Agent",
    "🎙️ Voice Assistant",
    "📄 Document Intelligence",
    "📊 Analytics AI",
    "🛡️ Security AI",
]
feature = st.sidebar.selectbox("Choose Feature", FEATURES)
st.sidebar.markdown("---")
st.sidebar.caption("NAS AI Platform · Powered by Ollama")

# ── Ollama status ────────────────────────────────────────────────────────────
from utils.llm import ollama_available
if not ollama_available():
    st.sidebar.error("⚠️ Ollama offline\n\nRun: `ollama serve`")
else:
    st.sidebar.success("✅ Ollama connected")


# ════════════════════════════════════════════════════════════════════════════
# 1. RAG ASSISTANT
# ════════════════════════════════════════════════════════════════════════════
if feature == FEATURES[0]:
    st.title("🔍 RAG Assistant")
    from modules.rag import ingest, run_rag, clear_store, store_size

    col1, col2 = st.columns([2, 1])
    with col1:
        uploaded = st.file_uploader("Upload a .txt file to build knowledge base", type=["txt"])
        if uploaded:
            text = uploaded.read().decode("utf-8", errors="ignore")
            if st.button("Ingest Document"):
                with st.spinner("Ingesting…"):
                    n = ingest(text)
                st.success(f"✅ Ingested {n} chunks.")

    with col2:
        st.metric("Chunks in store", store_size())
        if st.button("🗑️ Clear Store"):
            clear_store()
            st.rerun()

    st.divider()
    query = st.text_input("Ask a question about your documents")
    if st.button("Ask", key="rag_ask") and query:
        with st.spinner("Retrieving and generating…"):
            answer = run_rag(query)
        st.markdown("### Answer")
        st.write(answer)


# ════════════════════════════════════════════════════════════════════════════
# 2. TASK AGENT
# ════════════════════════════════════════════════════════════════════════════
elif feature == FEATURES[1]:
    st.title("🤖 Task Agent")
    from modules.task import plan_tasks, execute_task

    goal = st.text_area("Describe your goal", placeholder="e.g. Plan a product launch for a mobile app")
    col1, col2 = st.columns(2)
    with col1:
        plan_btn = st.button("📋 Plan Tasks")
    with col2:
        exec_btn = st.button("▶️ Execute First Task")

    if plan_btn and goal:
        with st.spinner("Planning…"):
            steps = plan_tasks(goal)
        st.session_state["task_steps"] = steps

    if "task_steps" in st.session_state:
        st.markdown("### Task Plan")
        for i, step in enumerate(st.session_state["task_steps"], 1):
            st.markdown(f"**{i}.** {step}")

    if exec_btn and "task_steps" in st.session_state:
        first = st.session_state["task_steps"][0] if st.session_state["task_steps"] else goal
        with st.spinner(f"Executing: {first}"):
            result = execute_task(first)
        st.markdown("### Execution Result")
        st.write(result)

    # ── Gmail compose ────────────────────────────────────────────────────────
    st.divider()
    with st.expander("📧 Send Email via Gmail"):
        from modules.gmail import gmail_available
        from modules.task import send_email_task
        ok, reason = gmail_available()
        if not ok:
            st.warning(
                f"Gmail not configured: *{reason}*\n\n"
                "**Setup:** Download your OAuth2 JSON from Google Cloud Console "
                "and save it as `credentials/gmail_oauth.json` in the project root. "
                "A browser will open once to authorise — token is cached automatically."
            )
        else:
            st.success("✅ Gmail connected")
        em_to      = st.text_input("To", placeholder="recipient@example.com")
        em_subject = st.text_input("Subject")
        em_body    = st.text_area("Body", height=120)
        if st.button("📤 Send Email") and em_to and em_subject:
            with st.spinner("Sending…"):
                em_result = send_email_task(em_to, em_subject, em_body)
            st.write(em_result)


# ════════════════════════════════════════════════════════════════════════════
# 3. VOICE ASSISTANT
# ════════════════════════════════════════════════════════════════════════════
elif feature == FEATURES[2]:
    st.title("🎙️ Voice Assistant")
    from modules.voice import transcribe, voice_chat, speak_reply, record_from_mic

    st.info("Record from microphone, upload an audio file, or type directly.")

    # ── Live mic recording ───────────────────────────────────────────────────
    col_mic, col_dur = st.columns([3, 1])
    with col_dur:
        rec_seconds = st.number_input("Duration (s)", min_value=2, max_value=30, value=5)
    with col_mic:
        if st.button("🎤 Record from Microphone"):
            try:
                with st.spinner(f"Recording for {rec_seconds}s… speak now!"):
                    audio_bytes = record_from_mic(seconds=int(rec_seconds))
                with st.spinner("Transcribing…"):
                    transcript = transcribe(audio_bytes, "mic.wav")
                st.session_state["transcript"] = transcript
                st.success("Recording complete.")
            except RuntimeError as e:
                st.error(str(e))

    st.divider()

    # ── File upload ──────────────────────────────────────────────────────────
    audio_file = st.file_uploader("Or upload audio file", type=["wav", "mp3", "ogg", "m4a"])
    if audio_file:
        audio_bytes = audio_file.read()
        if st.button("Transcribe File"):
            with st.spinner("Transcribing…"):
                transcript = transcribe(audio_bytes, audio_file.name)
            st.session_state["transcript"] = transcript

    if "transcript" in st.session_state:
        st.text_area("Transcript", st.session_state["transcript"], key="trans_display")

    typed = st.text_input("Or type your message directly")
    input_text = typed or st.session_state.get("transcript", "")

    if st.button("💬 Get Reply") and input_text:
        with st.spinner("Thinking…"):
            reply = voice_chat(input_text)
        st.markdown("### Assistant Reply")
        st.write(reply)
        audio_data = speak_reply(reply)
        if audio_data:
            st.audio(audio_data, format="audio/wav")
        else:
            st.caption("TTS not available — install `pyttsx3` (offline) or `gtts` (online)")


# ════════════════════════════════════════════════════════════════════════════
# 4. DOCUMENT INTELLIGENCE
# ════════════════════════════════════════════════════════════════════════════
elif feature == FEATURES[3]:
    st.title("📄 Document Intelligence")
    from modules.docint import extract_text, summarize, answer_question, extract_entities

    uploaded = st.file_uploader("Upload document (txt, pdf, docx)", type=["txt", "pdf", "docx"])

    if uploaded:
        file_bytes = uploaded.read()
        with st.spinner("Extracting text…"):
            text = extract_text(file_bytes, uploaded.name)
        st.session_state["doc_text"] = text
        with st.expander("📃 Extracted Text Preview"):
            st.text(text[:2000] + ("…" if len(text) > 2000 else ""))

    if "doc_text" in st.session_state:
        doc_text = st.session_state["doc_text"]
        tab1, tab2, tab3 = st.tabs(["Summarize", "Q&A", "Entities"])

        with tab1:
            style = st.radio("Summary style", ["brief", "detailed", "bullets"], horizontal=True)
            if st.button("Summarize"):
                with st.spinner("Summarizing…"):
                    st.write(summarize(doc_text, style))

        with tab2:
            q = st.text_input("Ask a question about the document")
            if st.button("Answer") and q:
                with st.spinner("Answering…"):
                    st.write(answer_question(doc_text, q))

        with tab3:
            if st.button("Extract Entities"):
                with st.spinner("Extracting…"):
                    st.write(extract_entities(doc_text))


# ════════════════════════════════════════════════════════════════════════════
# 5. ANALYTICS AI
# ════════════════════════════════════════════════════════════════════════════
elif feature == FEATURES[4]:
    st.title("📊 Analytics AI")
    from modules.analytics import nl_to_sql, run_query, explain_results, create_demo_db, _get_schema
    import sqlite3

    st.info("Uses a built-in demo SQLite database. Tables: `sales`, `users`.")
    db_path = create_demo_db()

    conn = sqlite3.connect(db_path)
    schema = _get_schema(conn)
    conn.close()

    with st.expander("📐 Database Schema"):
        st.code(schema)

    question = st.text_input("Ask a question in plain English", placeholder="e.g. Total sales by region")

    if st.button("Run Query") and question:
        with st.spinner("Converting to SQL…"):
            sql = nl_to_sql(question, schema)
        st.code(sql, language="sql")

        try:
            with st.spinner("Running query…"):
                df = run_query(db_path, sql)
            st.dataframe(df, use_container_width=True)

            with st.spinner("Explaining results…"):
                explanation = explain_results(question, df)
            st.markdown("### 💡 Insight")
            st.write(explanation)

            if len(df.columns) >= 2:
                try:
                    st.bar_chart(df.set_index(df.columns[0])[df.columns[1]])
                except Exception:
                    pass
        except Exception as e:
            st.error(f"Query error: {e}")


# ════════════════════════════════════════════════════════════════════════════
# 6. SECURITY AI
# ════════════════════════════════════════════════════════════════════════════
elif feature == FEATURES[5]:
    st.title("🛡️ Security AI")
    from modules.security import analyze_logs, classify_threat, generate_report, SAMPLE_LOGS

    tab1, tab2, tab3 = st.tabs(["Log Analyzer", "Threat Classifier", "Report Generator"])

    with tab1:
        log_input = st.text_area("Paste logs here", value=SAMPLE_LOGS, height=200)
        if st.button("Analyze Logs"):
            with st.spinner("Analyzing…"):
                result = analyze_logs(log_input)
            st.markdown("### 🔎 Analysis")
            st.write(result)

    with tab2:
        event = st.text_input("Describe a security event", placeholder="e.g. 15 failed SSH logins in 30 seconds from 192.168.1.45")
        if st.button("Classify Threat") and event:
            with st.spinner("Classifying…"):
                result = classify_threat(event)
            sev = result.get("severity", "?")
            color = {"Critical": "🔴", "High": "🟠", "Medium": "🟡", "Low": "🟢"}.get(sev, "⚪")
            st.markdown(f"**Severity:** {color} {sev}")
            st.markdown(f"**Type:** {result.get('threat_type', '?')}")
            st.markdown(f"**Confidence:** {result.get('confidence', '?')}%")
            st.markdown(f"**Description:** {result.get('description', '')}")

    with tab3:
        log_rep = st.text_area("Paste logs for report", value=SAMPLE_LOGS, height=150, key="rep_logs")
        if st.button("Generate Report"):
            with st.spinner("Generating…"):
                report = generate_report(log_rep)
            st.markdown("### 📋 Security Report")
            st.write(report)
