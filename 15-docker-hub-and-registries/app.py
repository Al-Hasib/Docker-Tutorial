"""Notes API — v6.

Same routes and cache-aside behavior as topic 12. The only change is that
every setting (DB connection, cache connection, TTL, debug mode) now flows
through config.py, which reads it from the environment — see the README for
where those environment values actually come from.
"""
from flask import Flask, jsonify, request, abort

import cache
import db
from config import Config

app = Flask(__name__)
db.init_db()


@app.get("/health")
def health():
    return jsonify(status="ok")


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
    return "", 204


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=Config.DEBUG)
