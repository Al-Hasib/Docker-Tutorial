# 11 · Docker Compose

## Learning objectives

- Read and write a `docker-compose.yml` with more than one service.
- Replace manual `docker network create` + several `docker run` commands with `docker compose up`.
- Understand `depends_on`'s real (limited) meaning, and why the app still needs retry logic.

## What changed in the app

Storage moves from SQLite (topic 9) to real **PostgreSQL**, run as its own service. `db.py` now
talks to Postgres over the network via `psycopg2`, using connection details from environment
variables that `docker-compose.yml` supplies.

## Why Compose

Manually, running this two-service app would mean:

```bash
docker network create notes-net
docker run -d --name db --network notes-net -e POSTGRES_DB=notes -e POSTGRES_USER=notes \
  -e POSTGRES_PASSWORD=notes -v notes-db-data:/var/lib/postgresql/data postgres:16
docker build -t notes-api .
docker run -d --name api --network notes-net -p 5000:5000 \
  -e POSTGRES_HOST=db -e POSTGRES_DB=notes -e POSTGRES_USER=notes -e POSTGRES_PASSWORD=notes \
  notes-api
```

That's exactly what topic 10 did by hand for two services. Docker Compose lets you describe the
same thing **declaratively**, once, in a file — and manage the whole stack with one command.

## The compose file

```yaml
services:
  api:
    build: .
    ports:
      - "5000:5000"
    environment:
      POSTGRES_HOST: db
      # ...
    depends_on:
      - db

  db:
    image: postgres:16
    environment:
      POSTGRES_DB: notes
      # ...
    volumes:
      - notes-db-data:/var/lib/postgresql/data

volumes:
  notes-db-data:
```

- Each entry under `services:` becomes a container.
- Compose automatically creates a **user-defined bridge network** (see topic 10) for the whole
  file and attaches every service to it — that's *why* `POSTGRES_HOST: db` just works: `db` is
  resolvable by name, no manual `docker network create` needed.
- `volumes:` at the top level declares the named volume; `db`'s `volumes:` entry mounts it, exactly
  like `-v` did in topic 9.
- `depends_on: - db` only guarantees the `db` **container** starts before `api` starts — it does
  **not** wait for Postgres to finish initializing inside that container. That gap is exactly why
  `db.py`'s `init_db()` retries the connection a few times instead of assuming success immediately.

## Demo

```bash
cd 11-docker-compose

docker compose up --build -d
docker compose ps
```

```bash
curl http://localhost:5000/health
curl -X POST http://localhost:5000/notes -H "Content-Type: application/json" -d '{"text":"Stored in Postgres now"}'
curl http://localhost:5000/notes
```

```bash
# Logs from a specific service, or everything
docker compose logs api
docker compose logs -f

# A shell inside a running service
docker compose exec db psql -U notes -d notes -c "SELECT * FROM notes;"
```

**Stop vs. tear down:**

```bash
docker compose stop      # stop containers, keep them (and the volume) around
docker compose start     # start them again

docker compose down      # remove containers AND the network (volume survives by default)
docker compose down -v   # also delete the named volume — the notes are gone for good
```

## Cheat sheet

| Command | What it does |
|---|---|
| `docker compose up [-d] [--build]` | Create + start every service |
| `docker compose ps` | List services in this project |
| `docker compose logs [-f] [service]` | View logs |
| `docker compose exec service CMD` | Run a command in a running service |
| `docker compose stop` / `start` | Stop/start without removing anything |
| `docker compose down [-v]` | Remove containers + network (and volumes with `-v`) |

## Key takeaways

- One `docker-compose.yml` replaces a whole sequence of `docker network`/`docker run` commands.
- Compose gives every service name-based DNS automatically — no manual network setup.
- `depends_on` is about container start order, not "readiness" — real apps still need their own
  retry/backoff logic against dependent services.

## Exercise

Add a `restart: unless-stopped` line to the `db` service, run `docker compose up -d`, then kill the
Postgres process from inside its container (`docker compose exec db kill 1`) and watch Compose
restart it automatically. This previews the restart-policy work in
[19-production-deployment](../19-production-deployment).

## Up next

[12 · Multi-Container Apps](../12-multi-container-apps) — adding a Redis cache as a third service.
