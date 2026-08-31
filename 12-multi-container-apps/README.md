# 12 · Multi-Container Apps

## Learning objectives

- Add a third service (Redis) to a Compose stack and wire it up correctly.
- Implement the cache-aside pattern: check cache → miss → read DB → populate cache.
- Watch, live, how caching changes response source and speed.

## What changed in the app

A `cache` service (Redis) sits in front of `GET /notes`. `cache.py` implements a simple
**cache-aside** pattern:

1. On `GET /notes`: check Redis first. Hit → return immediately, `"source": "cache"`.
2. On miss: query Postgres, store the result in Redis with a 10-second TTL, return it,
   `"source": "database"`.
3. On any write (`POST`/`DELETE`): delete the cached key, so the next read is forced back to the
   database and picks up the change.

This is the same three-service shape used by a huge number of real-world web apps: **app + a
relational database + a cache**.

## The compose file

```yaml
services:
  api:
    build: .
    environment:
      POSTGRES_HOST: db
      REDIS_HOST: cache
    depends_on: [db, cache]

  db:
    image: postgres:16
    volumes: [notes-db-data:/var/lib/postgresql/data]

  cache:
    image: redis:7-alpine
```

Notice `cache` gets **no volume** — losing cached data is fine (it's just a cache, the source of
truth is Postgres), so we deliberately let it stay ephemeral. That's a real design decision, not an
oversight: not every service in a stack needs persistence.

## Demo

```bash
cd 12-multi-container-apps
docker compose up --build -d
docker compose ps    # three services: api, db, cache
```

```bash
# Seed a note
curl -X POST http://localhost:5000/notes -H "Content-Type: application/json" -d '{"text":"Cache me if you can"}'

# First GET after a write: cache was just invalidated -> "source": "database"
curl http://localhost:5000/notes

# GET again immediately: "source": "cache"
curl http://localhost:5000/notes

# Wait past the 10s TTL, then GET again: back to "source": "database"
sleep 11
curl http://localhost:5000/notes
```

**Watch the cache directly:**

```bash
docker compose exec cache redis-cli GET notes:all
docker compose exec cache redis-cli TTL notes:all
```

**Prove invalidation on write:**

```bash
curl http://localhost:5000/notes   # warm the cache -> "source": "cache" on the next call
curl -X POST http://localhost:5000/notes -H "Content-Type: application/json" -d '{"text":"invalidate me"}'
docker compose exec cache redis-cli GET notes:all   # (nil) — the write deleted the cached key
```

## Key takeaways

- Compose scales to N services the same way it scales to 2 — just add another entry.
- A cache doesn't need a volume; ephemeral is often the *correct* choice, not a missing feature.
- Cache-aside is simple: read-through on miss, invalidate on write. Getting invalidation right is
  the entire difficulty of caching — this app's approach (delete-on-write) is the simplest correct
  one.

## Exercise

Change `CACHE_TTL_SECONDS` in `cache.py` to `60`, rebuild, and use `docker stats` to compare CPU
usage on the `db` container under repeated `GET /notes` calls with a 10s TTL vs. a 60s TTL — a
longer TTL means fewer database hits, at the cost of staler data for longer.

## Up next

[13 · Environment Variables & Config](../13-environment-variables-and-config) — moving all these
hardcoded values into proper configuration.
