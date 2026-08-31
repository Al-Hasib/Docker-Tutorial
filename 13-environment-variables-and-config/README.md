# 13 · Environment Variables & Config

## Learning objectives

- Centralize config reads into one module instead of scattering `os.environ.get()` everywhere.
- Use a `.env` file with Docker Compose, and understand `env_file:` vs. `environment:` precedence.
- Draw the line between "config that changes per environment" and "structural, network-level
  values."

## What changed in the app

Every setting the app reads from the environment now flows through one file, `config.py`. `db.py`,
`cache.py`, and `app.py` all import `Config` instead of calling `os.environ.get(...)` inline. This
is a plain Python habit (nothing Docker-specific about it) — but it makes the *next* part obvious:
exactly which environment variables this app needs, in one place.

## `.env` + `.env.example`

- **`.env`** — the actual local values. Already covered by this repo's root `.gitignore`, so it's
  never committed. This is where real secrets would go on a real project.
- **`.env.example`** — committed, documents every variable with safe placeholder values, and is
  the file new teammates copy: `cp .env.example .env`.

```bash
cp .env.example .env
```

## Wiring `.env` into Compose

```yaml
services:
  api:
    env_file:
      - .env
    environment:
      POSTGRES_HOST: db
      REDIS_HOST: cache
```

Two different mechanisms, deliberately combined:

- **`env_file:`** loads every key from `.env` into the container's environment — this is where
  `POSTGRES_PASSWORD`, `CACHE_TTL_SECONDS`, etc. come from.
- **`environment:`** sets values directly in the compose file, and **overrides** anything with the
  same key from `env_file:`.

`POSTGRES_HOST` and `REDIS_HOST` are set only in `environment:`, never in `.env`, on purpose: they
depend on the Compose network topology (the service names `db` and `cache`), not on who's deploying
the app. Mixing that up — e.g. letting a developer's `.env` accidentally set `POSTGRES_HOST` to
something else — is a common, confusing bug. Keep "where to connect" (structural, belongs in
`docker-compose.yml`) separate from "what to connect with" (secrets/tuning, belongs in `.env`).

## Demo

```bash
cd 13-environment-variables-and-config
cp .env.example .env

docker compose up --build -d
curl http://localhost:5000/health
```

**Prove `.env` is actually driving behavior** — change the cache TTL without touching any code:

```bash
# Edit .env: CACHE_TTL_SECONDS=60
docker compose up -d --force-recreate api
docker compose exec cache redis-cli TTL notes:all   # after one GET /notes, TTL should read ~60
```

**Prove `environment:` wins over `env_file:`** — add `POSTGRES_HOST=something-else` to `.env`,
then:

```bash
docker compose up -d --force-recreate api
docker compose exec api python -c "from config import Config; print(Config.POSTGRES_HOST)"
# still prints "db" — docker-compose.yml's environment: takes precedence
```

Remove that test line from `.env` afterward.

## Key takeaways

- One `config.py` (or equivalent) beats `os.environ.get()` sprinkled across the codebase — you can
  see every setting the app depends on in one place.
- `.env` (gitignored, real values) + `.env.example` (committed, documented placeholders) is the
  standard pattern for local secrets.
- In Compose, `environment:` overrides `env_file:` for the same key — useful for values that must
  stay fixed regardless of what's in a developer's `.env`.

## Exercise

Add a new setting — e.g. `MAX_NOTE_LENGTH` — to `config.py` and `.env.example`, then enforce it in
`create_note()` (reject notes longer than that with a 400). Confirm changing the value in `.env`
and recreating the `api` service changes the enforced limit without touching `app.py`.

## Up next

[14 · Multi-Stage Builds](../14-multi-stage-builds) — shrinking the image itself.
