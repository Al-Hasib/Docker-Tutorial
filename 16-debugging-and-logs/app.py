"""Notes API — v7.

Same routes as topic 13, plus:
  - structured logging to stdout (which is exactly what `docker logs` shows)
  - a REAL /health check that verifies the database and cache are actually
    reachable, instead of always returning "ok"
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
db.init_db()


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
    app.run(host="0.0.0.0", port=5000, debug=Config.DEBUG)
