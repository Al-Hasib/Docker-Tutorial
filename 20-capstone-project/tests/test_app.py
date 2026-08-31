"""Tests for the Notes API.

No real Postgres or Redis needed: db.get_connection / cache functions are
monkeypatched with lightweight fakes, so these run anywhere, instantly —
including inside the "tester" Docker build stage in CI.
"""
import cache
import db
from app import app as flask_app


class FakeCursor:
    """Mimics just enough of psycopg2's RealDictCursor for these tests."""

    def __init__(self, rows=None, one=None):
        self._rows = rows if rows is not None else []
        self._one = one
        self.rowcount = len(self._rows) if rows is not None else (1 if one else 0)

    def execute(self, query, params=None):
        pass

    def fetchall(self):
        return self._rows

    def fetchone(self):
        return self._one

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


class FakeConnection:
    def __init__(self, cursor: FakeCursor):
        self._cursor = cursor
        self.committed = False

    def cursor(self):
        return self._cursor

    def commit(self):
        self.committed = True

    def close(self):
        pass


def make_client(monkeypatch):
    # Safe no-op cache by default; individual tests override as needed.
    monkeypatch.setattr(cache, "get_cached_notes", lambda: None)
    monkeypatch.setattr(cache, "set_cached_notes", lambda notes: None)
    monkeypatch.setattr(cache, "invalidate_notes_cache", lambda: None)
    flask_app.testing = True
    return flask_app.test_client()


def test_create_note_requires_text(monkeypatch):
    client = make_client(monkeypatch)
    resp = client.post("/notes", json={})
    assert resp.status_code == 400


def test_create_note_success(monkeypatch):
    client = make_client(monkeypatch)
    monkeypatch.setattr(db, "get_connection", lambda: FakeConnection(FakeCursor(one={"id": 1})))

    resp = client.post("/notes", json={"text": "Learn Docker CI/CD"})

    assert resp.status_code == 201
    body = resp.get_json()
    assert body == {"id": 1, "text": "Learn Docker CI/CD"}


def test_list_notes_served_from_cache(monkeypatch):
    client = make_client(monkeypatch)
    monkeypatch.setattr(cache, "get_cached_notes", lambda: [{"id": 1, "text": "cached note"}])

    resp = client.get("/notes")

    assert resp.status_code == 200
    body = resp.get_json()
    assert body["source"] == "cache"
    assert body["notes"] == [{"id": 1, "text": "cached note"}]


def test_list_notes_falls_back_to_database_on_cache_miss(monkeypatch):
    client = make_client(monkeypatch)
    rows = [{"id": 1, "text": "from the db"}]
    monkeypatch.setattr(db, "get_connection", lambda: FakeConnection(FakeCursor(rows=rows)))

    resp = client.get("/notes")

    assert resp.status_code == 200
    body = resp.get_json()
    assert body["source"] == "database"
    assert body["notes"] == rows


def test_get_note_not_found(monkeypatch):
    client = make_client(monkeypatch)
    monkeypatch.setattr(db, "get_connection", lambda: FakeConnection(FakeCursor(one=None)))

    resp = client.get("/notes/999")

    assert resp.status_code == 404


def test_delete_note_not_found(monkeypatch):
    client = make_client(monkeypatch)
    monkeypatch.setattr(db, "get_connection", lambda: FakeConnection(FakeCursor(rows=[])))

    resp = client.delete("/notes/999")

    assert resp.status_code == 404
