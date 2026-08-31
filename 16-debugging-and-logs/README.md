# 16 · Debugging & Logs

## Learning objectives

- Write logs that are actually useful for debugging a containerized app.
- Add a Dockerfile `HEALTHCHECK`, and a Compose `healthcheck:` that fixes topic 11's `depends_on`
  gap for real this time.
- Use `docker logs`, `docker exec`, `docker inspect`, `docker top`, and `docker stats` to debug a
  running container without ever "SSH-ing in" the old way.

## What changed in the app

- Every request is now logged (`method path -> status`) via Flask's `after_request` hook, using
  Python's standard `logging` module configured to print to **stdout**.
- `/health` now actually checks the database and cache connections instead of unconditionally
  returning `"ok"` — it returns `503` if either dependency is unreachable.

**Why stdout, specifically?** Docker captures whatever a container writes to stdout/stderr and
that's exactly what `docker logs` shows you. Writing logs to a file *inside* the container is a
trap — that file disappears with the container (topic 9) and `docker logs` won't show it.

## Fixing `depends_on` for real

Topic 11 noted `depends_on` only waits for a container to *start*, not to be *ready*. This topic
fixes that properly using **healthchecks**:

```yaml
db:
  healthcheck:
    test: ["CMD-SHELL", "pg_isready -U $$POSTGRES_USER -d $$POSTGRES_DB"]
    interval: 5s

api:
  depends_on:
    db:
      condition: service_healthy
```

Now `api` genuinely waits until `db`'s healthcheck passes — not just until the container process
starts — before Compose starts it. (The retry logic in `db.py` from topic 11 is still good defense
in depth, and is exactly what's protecting the app during the brief startup window regardless.)

## The Dockerfile `HEALTHCHECK`

```dockerfile
HEALTHCHECK --interval=10s --timeout=3s --start-period=5s --retries=3 \
  CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://localhost:5000/health').status == 200 else 1)"
```

Docker runs this command *inside* the container every 10 seconds. Three consecutive failures marks
the container `unhealthy` — visible directly in `docker ps`.

## Demo

```bash
cd 16-debugging-and-logs
cp .env.example .env
docker compose up --build -d

docker ps   # STATUS column shows "(healthy)" once the healthcheck passes
```

**Logs:**

```bash
curl -X POST http://localhost:5000/notes -H "Content-Type: application/json" -d '{"text":"debug me"}'
docker compose logs -f api
# 2026-... INFO notes-api: POST /notes -> 201
```

**Break something on purpose and watch health degrade:**

```bash
docker compose stop cache
curl http://localhost:5000/health
# {"status": "degraded", "checks": {"database": true, "cache": false}}  (HTTP 503)

docker compose start cache
curl http://localhost:5000/health   # back to "ok"
```

**Inspect health history directly:**

```bash
docker inspect --format '{{json .State.Health}}' $(docker compose ps -q api) | python -m json.tool
```

**Other debugging commands worth knowing:**

```bash
docker top $(docker compose ps -q api)      # processes running inside the container
docker stats                                 # live CPU/mem/network for every container
docker events                                # live stream of Docker's own lifecycle events
docker exec -it $(docker compose ps -q api) /bin/bash   # poke around directly
```

## Key takeaways

- Log to stdout/stderr, always — `docker logs` only sees what a container writes there.
- A `HEALTHCHECK`/`healthcheck:` turns "is it actually working" from a guess into a status Docker
  tracks for you, visible in `docker ps` and usable by `depends_on: condition: service_healthy`.
- `docker top`, `docker stats`, and `docker inspect` answer "what's this container doing right now"
  without needing your own custom tooling.

## Exercise

Add a `/debug/slow` route that `time.sleep(5)`s before responding, hit it a few times, then use
`docker stats` in one terminal and repeated requests in another to watch CPU/network activity
correlate in real time.

## Up next

[17 · Docker Security Best Practices](../17-docker-security-best-practices) — hardening this image
before it goes anywhere near production.
