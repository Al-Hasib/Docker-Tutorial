"""Postgres data-access layer for the Notes API — now reading connection
details from config.py instead of os.environ directly.
"""
import time

import psycopg2
from psycopg2.extras import RealDictCursor

from config import Config


def get_connection():
    return psycopg2.connect(
        host=Config.POSTGRES_HOST,
        dbname=Config.POSTGRES_DB,
        user=Config.POSTGRES_USER,
        password=Config.POSTGRES_PASSWORD,
        cursor_factory=RealDictCursor,
    )


def init_db(retries: int = 10, delay: float = 2.0) -> None:
    """Create the notes table, retrying while Postgres is still starting up."""
    last_err = None
    for _ in range(retries):
        try:
            conn = get_connection()
            conn.autocommit = True
            with conn.cursor() as cur:
                cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS notes (
                        id SERIAL PRIMARY KEY,
                        text TEXT NOT NULL
                    )
                    """
                )
            conn.close()
            return
        except psycopg2.OperationalError as exc:
            last_err = exc
            time.sleep(delay)
    raise RuntimeError(f"Could not connect to Postgres after {retries} retries") from last_err
