"""Analytics AI: natural language → SQL → execute → explain results."""
from __future__ import annotations
import sqlite3
import json
import pathlib
import pandas as pd
from utils.llm import chat


def _get_schema(conn: sqlite3.Connection) -> str:
    cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [r[0] for r in cursor.fetchall()]
    schema_parts = []
    for table in tables:
        cols = conn.execute(f"PRAGMA table_info({table})").fetchall()
        col_str = ", ".join(f"{c[1]} {c[2]}" for c in cols)
        schema_parts.append(f"{table}({col_str})")
    return "\n".join(schema_parts)


def nl_to_sql(question: str, schema: str) -> str:
    system = (
        "You are an expert SQL assistant. Given a database schema, convert the user's "
        "question into a valid SQLite SELECT query. Return ONLY the SQL, no explanation."
    )
    prompt = f"Schema:\n{schema}\n\nQuestion: {question}"
    return chat(prompt, system).strip().strip("```sql").strip("```").strip()


def run_query(db_path: str, sql: str) -> pd.DataFrame:
    conn = sqlite3.connect(db_path)
    try:
        df = pd.read_sql_query(sql, conn)
        return df
    finally:
        conn.close()


def explain_results(question: str, df: pd.DataFrame) -> str:
    system = "Explain these query results in plain English. Be concise and insightful."
    data_str = df.to_string(index=False) if not df.empty else "No results returned."
    prompt = f"Original question: {question}\n\nResults:\n{data_str}"
    return chat(prompt, system)


def create_demo_db(db_path: str = "") -> str:
    """Create a sample SQLite DB for demo purposes.

    Uses a user-writable path that works on Windows, macOS, and Linux.
    The parent directory is created if it does not exist.
    """
    if not db_path:
        # pathlib.Path.home() is safe on all platforms; avoids /tmp on Windows
        db_path = str(pathlib.Path.home() / ".nas_ai" / "demo_analytics.db")

    # Ensure the parent directory exists before SQLite tries to open the file
    pathlib.Path(db_path).parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(db_path)
    conn.executescript("""
        DROP TABLE IF EXISTS sales;
        CREATE TABLE sales (
            id INTEGER PRIMARY KEY,
            product TEXT,
            region TEXT,
            amount REAL,
            date TEXT
        );
        INSERT INTO sales VALUES
          (1,'Widget A','North',1200.0,'2024-01-15'),
          (2,'Widget B','South',850.0,'2024-01-20'),
          (3,'Widget A','East',1500.0,'2024-02-01'),
          (4,'Gadget X','North',2300.0,'2024-02-10'),
          (5,'Gadget X','South',1900.0,'2024-03-05'),
          (6,'Widget B','East',760.0,'2024-03-12'),
          (7,'Widget A','West',1100.0,'2024-04-01'),
          (8,'Gadget X','West',2100.0,'2024-04-15');

        DROP TABLE IF EXISTS users;
        CREATE TABLE users (
            id INTEGER PRIMARY KEY,
            name TEXT,
            region TEXT,
            signup_date TEXT
        );
        INSERT INTO users VALUES
          (1,'Alice','North','2023-06-01'),
          (2,'Bob','South','2023-08-15'),
          (3,'Carol','East','2023-11-20'),
          (4,'Dave','West','2024-01-05');
    """)
    conn.commit()
    conn.close()
    return db_path
