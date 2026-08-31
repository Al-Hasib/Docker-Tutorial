"""Single place every setting is read from the environment.

Nothing here is Docker-specific — but Docker (via `docker-compose.yml`'s
`environment:` and `env_file:`) is what actually supplies these values at
container-start time. See the README for where each value comes from and
why.
"""
import os


class Config:
    # --- Postgres ---
    POSTGRES_HOST = os.environ.get("POSTGRES_HOST", "db")
    POSTGRES_DB = os.environ.get("POSTGRES_DB", "notes")
    POSTGRES_USER = os.environ.get("POSTGRES_USER", "notes")
    POSTGRES_PASSWORD = os.environ.get("POSTGRES_PASSWORD", "notes")

    # --- Redis ---
    REDIS_HOST = os.environ.get("REDIS_HOST", "cache")
    REDIS_PORT = int(os.environ.get("REDIS_PORT", "6379"))
    CACHE_TTL_SECONDS = int(os.environ.get("CACHE_TTL_SECONDS", "10"))

    # --- Flask ---
    DEBUG = os.environ.get("FLASK_DEBUG", "false").lower() == "true"
