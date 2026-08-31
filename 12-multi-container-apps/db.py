"""Postgres data-access layer for the Notes API.

Storage moves from SQLite (topic 9) to a real PostgreSQL database, running
as its own container/service. Connection details come from environment
variables — docker-compose.yml is what actually sets them (see topic 13 for
a deeper look at env-based config).
"""
import os
import time

import psycopg2
from psycopg2.extras import RealDictCursor


def get_connection():
    return psycopg2.connect(
        host=os.environ.get("POSTGRES_HOST", "db"),
        dbname=os.environ.get("POSTGRES_DB", "notes"),
        user=os.environ.get("POSTGRES_USER", "notes"),
        password=os.environ.get("POSTGRES_PASSWORD", "notes"),
        cursor_factory=RealDictCursor,
    )


def init_db(retries: int = 10, delay: float = 2.0) -> None:
    """Create the notes table, retrying while Postgres is still starting up.

    `depends_on` in docker-compose.yml only waits for the db CONTAINER to
    start, not for Postgres itself to finish initializing — so the API can
    boot before Postgres is ready to accept connections. Retrying here is a
    simple, honest fix.
    """
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
