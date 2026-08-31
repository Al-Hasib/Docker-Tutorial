"""Notes API — v8.

Same routes and behavior as topic 16. The only change: `db.init_db()` and
`app.run()` now happen ONLY when this file is executed directly, not on
import. That's what lets `tests/test_app.py` import `app` and exercise its
routes without needing a live Postgres/Redis connection at import time.
"""
import logging

from flask import Flask, jsonify, request, abort

import cache
import db
from config import Config

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger("notes-api")

app = Flask(__name__)


@app.after_request
def log_request(response):
    logger.info("%s %s -> %s", request.method, request.path, response.status_code)
    return response


@app.get("/health")
def health():
    checks = {"database": False, "cache": False}

    try:
        conn = db.get_connection()
        conn.close()
        checks["database"] = True
    except Exception:
        logger.exception("Database health check failed")

    try:
        cache.get_client().ping()
        checks["cache"] = True
    except Exception:
        logger.exception("Cache health check failed")

    healthy = all(checks.values())
    return jsonify(status="ok" if healthy else "degraded", checks=checks), (200 if healthy else 503)


@app.get("/notes")
def list_notes():
    cached = cache.get_cached_notes()
    if cached is not None:
        return jsonify({"source": "cache", "notes": cached})

    conn = db.get_connection()
    with conn.cursor() as cur:
        cur.execute("SELECT id, text FROM notes ORDER BY id")
        rows = cur.fetchall()
    conn.close()

    cache.set_cached_notes(rows)
    return jsonify({"source": "database", "notes": rows})


@app.post("/notes")
def create_note():
    data = request.get_json(silent=True) or {}
    text = data.get("text")
    if not text:
        abort(400, description="'text' field is required")

    conn = db.get_connection()
    with conn.cursor() as cur:
        cur.execute("INSERT INTO notes (text) VALUES (%s) RETURNING id", (text,))
        note_id = cur.fetchone()["id"]
    conn.commit()
    conn.close()

    cache.invalidate_notes_cache()
    logger.info("Created note id=%s", note_id)
    return jsonify({"id": note_id, "text": text}), 201


@app.get("/notes/<int:note_id>")
def get_note(note_id):
    conn = db.get_connection()
    with conn.cursor() as cur:
        cur.execute("SELECT id, text FROM notes WHERE id = %s", (note_id,))
        row = cur.fetchone()
    conn.close()
    if row is None:
        abort(404, description="Note not found")
    return jsonify(row)


@app.delete("/notes/<int:note_id>")
def delete_note(note_id):
    conn = db.get_connection()
    with conn.cursor() as cur:
        cur.execute("DELETE FROM notes WHERE id = %s", (note_id,))
        deleted = cur.rowcount
    conn.commit()
    conn.close()

    if deleted == 0:
        abort(404, description="Note not found")

    cache.invalidate_notes_cache()
    logger.info("Deleted note id=%s", note_id)
    return "", 204


if __name__ == "__main__":
    db.init_db()
    app.run(host="0.0.0.0", port=5000, debug=Config.DEBUG)
