"""Notes API — v1.

A tiny in-memory REST API for notes. This is the app the rest of the course
builds on, one Docker concept at a time. Storage here is just a Python list,
so all notes disappear when the container stops — topic 9 (Volumes) fixes
that.
"""
from flask import Flask, jsonify, request, abort

app = Flask(__name__)

notes = []
next_id = 1


@app.get("/health")
def health():
    return jsonify(status="ok")


@app.get("/notes")
def list_notes():
    return jsonify(notes)


@app.post("/notes")
def create_note():
    global next_id
    data = request.get_json(silent=True) or {}
    text = data.get("text")
    if not text:
        abort(400, description="'text' field is required")

    note = {"id": next_id, "text": text}
    notes.append(note)
    next_id += 1
    return jsonify(note), 201


@app.get("/notes/<int:note_id>")
def get_note(note_id):
    note = next((n for n in notes if n["id"] == note_id), None)
    if note is None:
        abort(404, description="Note not found")
    return jsonify(note)


@app.delete("/notes/<int:note_id>")
def delete_note(note_id):
    global notes
    before = len(notes)
    notes = [n for n in notes if n["id"] != note_id]
    if len(notes) == before:
        abort(404, description="Note not found")
    return "", 204


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
