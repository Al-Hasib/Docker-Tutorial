"""Tiny SQLite data-access layer for the Notes API.

The database file lives at /app/data/notes.db INSIDE the container. On its
own that's just as ephemeral as the old in-memory list — the trick is
mounting /app/data to a Docker volume so the file survives container
restarts and even `docker rm`. See the README for the exact commands.
"""
import sqlite3
from pathlib import Path

DB_PATH = Path("/app/data/notes.db")


def get_connection():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text TEXT NOT NULL
        )
        """
    )
    conn.commit()
    conn.close()
