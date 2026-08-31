"""Notes API — v2.

Same routes as v1, but notes are now persisted to a SQLite file at
/app/data/notes.db instead of an in-memory list, via db.py. See the README
for why this alone isn't enough to survive a container being removed — you
also need a Docker volume mounted at /app/data.
"""
from flask import Flask, jsonify, request, abort

import db

app = Flask(__name__)
db.init_db()


@app.get("/health")
def health():
    return jsonify(status="ok")


@app.get("/notes")
def list_notes():
    conn = db.get_connection()
    rows = conn.execute("SELECT id, text FROM notes ORDER BY id").fetchall()
    conn.close()
    return jsonify([dict(row) for row in rows])


@app.post("/notes")
def create_note():
    data = request.get_json(silent=True) or {}
    text = data.get("text")
    if not text:
        abort(400, description="'text' field is required")

    conn = db.get_connection()
    cur = conn.execute("INSERT INTO notes (text) VALUES (?)", (text,))
    conn.commit()
    note = {"id": cur.lastrowid, "text": text}
    conn.close()
    return jsonify(note), 201


@app.get("/notes/<int:note_id>")
def get_note(note_id):
    conn = db.get_connection()
    row = conn.execute("SELECT id, text FROM notes WHERE id = ?", (note_id,)).fetchone()
    conn.close()
    if row is None:
        abort(404, description="Note not found")
    return jsonify(dict(row))


@app.delete("/notes/<int:note_id>")
def delete_note(note_id):
    conn = db.get_connection()
    cur = conn.execute("DELETE FROM notes WHERE id = ?", (note_id,))
    conn.commit()
    conn.close()
    if cur.rowcount == 0:
        abort(404, description="Note not found")
    return "", 204


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
