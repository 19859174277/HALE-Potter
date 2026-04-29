import sqlite3
import json
import os
from datetime import datetime
from typing import List, Optional, Dict, Any

DB_DIR = os.path.join(os.path.dirname(__file__), "..")
DB_PATH = os.path.join(DB_DIR, "chat_history.db")

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    os.makedirs(DB_DIR, exist_ok=True)
    with get_conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                title TEXT,
                created_at TEXT
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                role TEXT,
                content TEXT,
                images TEXT,
                timestamp TEXT,
                FOREIGN KEY (session_id) REFERENCES sessions(session_id)
            )
        """)
        conn.commit()

def create_session(session_id: str, title: str = "New Chat"):
    with get_conn() as conn:
        conn.execute(
            "INSERT OR IGNORE INTO sessions (session_id, title, created_at) VALUES (?, ?, ?)",
            (session_id, title, datetime.now().isoformat()),
        )
        conn.commit()

def get_sessions() -> List[Dict[str, Any]]:
    with get_conn() as conn:
        rows = conn.execute("SELECT * FROM sessions ORDER BY created_at DESC").fetchall()
        return [dict(r) for r in rows]

def get_messages(session_id: str) -> List[Dict[str, Any]]:
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM messages WHERE session_id = ? ORDER BY id ASC",
            (session_id,),
        ).fetchall()
        return [dict(r) for r in rows]

def add_message(session_id: str, role: str, content: str, images: Optional[List[str]] = None):
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO messages (session_id, role, content, images, timestamp) VALUES (?, ?, ?, ?, ?)",
            (session_id, role, content, json.dumps(images or []), datetime.now().isoformat()),
        )
        conn.commit()

def update_session_title(session_id: str, title: str):
    with get_conn() as conn:
        conn.execute("UPDATE sessions SET title = ? WHERE session_id = ?", (title, session_id))
        conn.commit()

def delete_session(session_id: str):
    with get_conn() as conn:
        conn.execute("DELETE FROM messages WHERE session_id = ?", (session_id,))
        conn.execute("DELETE FROM sessions WHERE session_id = ?", (session_id,))
        conn.commit()
