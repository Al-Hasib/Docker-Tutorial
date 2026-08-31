"""Redis cache-aside helper — now reading its settings from config.py."""
import json

import redis

from config import Config

NOTES_CACHE_KEY = "notes:all"

_client = None


def get_client():
    global _client
    if _client is None:
        _client = redis.Redis(host=Config.REDIS_HOST, port=Config.REDIS_PORT, decode_responses=True)
    return _client


def get_cached_notes():
    raw = get_client().get(NOTES_CACHE_KEY)
    return json.loads(raw) if raw is not None else None


def set_cached_notes(notes) -> None:
    get_client().setex(NOTES_CACHE_KEY, Config.CACHE_TTL_SECONDS, json.dumps(notes))


def invalidate_notes_cache() -> None:
    get_client().delete(NOTES_CACHE_KEY)
