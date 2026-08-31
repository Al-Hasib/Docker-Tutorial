"""Redis cache-aside helper for the notes list.

Cache-aside pattern: on read, check the cache first; on miss, read the
database and populate the cache; on any write, invalidate the cached value
so the next read is forced back to the database.
"""
import json
import os

import redis

NOTES_CACHE_KEY = "notes:all"
CACHE_TTL_SECONDS = 10

_client = None


def get_client():
    global _client
    if _client is None:
        _client = redis.Redis(
            host=os.environ.get("REDIS_HOST", "cache"),
            port=int(os.environ.get("REDIS_PORT", 6379)),
            decode_responses=True,
        )
    return _client


def get_cached_notes():
    raw = get_client().get(NOTES_CACHE_KEY)
    return json.loads(raw) if raw is not None else None


def set_cached_notes(notes) -> None:
    get_client().setex(NOTES_CACHE_KEY, CACHE_TTL_SECONDS, json.dumps(notes))


def invalidate_notes_cache() -> None:
    get_client().delete(NOTES_CACHE_KEY)
