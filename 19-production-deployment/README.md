# 19 · Production Deployment

## Learning objectives

- Put a reverse proxy (Nginx) in front of the app instead of exposing it directly.
- Choose the right `restart:` policy for each kind of service.
- Cap CPU/memory per service so one container can't starve the whole host.
- Know the difference between this course's `docker-compose.yml` (dev) and `docker-compose.prod.yml`
  (production).

## Dev vs. prod compose files

|                 | `docker-compose.yml` (dev, from topic 17)             | `docker-compose.prod.yml` (this topic)                              |
| --------------- | ------------------------------------------------------- | --------------------------------------------------------------------- |
| Entry point     | `api` exposed directly on `localhost:5000`          | Only`nginx` exposed, on port 80 — `api` has no `ports:` at all |
| Restarts        | None specified (fine for a demo you start/stop by hand) | `restart: unless-stopped` everywhere                                |
| Resource limits | None                                                    | `deploy.resources.limits` per service                               |
| Reverse proxy   | None                                                    | Nginx in front of everything                                          |

Both describe the *same* logical stack (api + db + cache); the production file just adds the
operational concerns real deployments need.

## 1. Nginx as a reverse proxy

```nginx
upstream notes_api {
    server api:5000;
}
server {
    listen 80;
    location / {
        proxy_pass http://notes_api;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Why put anything in front of the app at all?

- A single, well-known **entry point** on port 80 (and, in a real deployment, 443 for TLS) — the
  app container itself is never exposed to the outside world.
- Nginx is what would terminate **TLS/HTTPS** in a real deployment (a certificate goes on Nginx,
  not on the Flask app).
- The `proxy_set_header` lines forward the real client IP and protocol through to the app — without
  them, the app would see every request as coming from Nginx itself.

## 2. Restart policies

| Policy             | Behavior                                                                                          |
| ------------------ | ------------------------------------------------------------------------------------------------- |
| `no` (default)   | Never restart automatically                                                                       |
| `on-failure`     | Restart only if the container exits with a non-zero code                                          |
| `always`         | Always restart, even after`docker stop` followed by a daemon restart                            |
| `unless-stopped` | Like`always`, but respects an explicit `docker stop` (won't restart until you start it again) |

`unless-stopped` is used throughout `docker-compose.prod.yml` — it's the standard choice for
long-running services: they come back after a crash or host reboot, but a deliberate `docker compose stop` is still respected.

## 3. Resource limits

```yaml
deploy:
  resources:
    limits:
      cpus: "0.50"
      memory: 256M
```

> Historically, `deploy:` only applied under Docker Swarm. Modern `docker compose up` (Compose v2)
> now applies `deploy.resources.limits` directly, even without Swarm — which is what lets this
> file work with a plain `docker compose up`.

Without limits, one runaway container (a memory leak, a traffic spike) can starve every other
container — and the host itself. Limits turn "one bad container" into "one *contained* bad
container."

## Demo

```bash
cd 19-production-deployment
cp .env.example .env

docker compose -f docker-compose.prod.yml up --build -d
docker compose -f docker-compose.prod.yml ps
```

```bash
# Everything goes through Nginx on port 80 now — not 5000
curl http://localhost/health
curl -X POST http://localhost/notes -H "Content-Type: application/json" -d '{"text":"Deployed via Nginx"}'
curl http://localhost/notes
```

**Confirm the API really isn't reachable directly:**

```bash
curl http://localhost:5000/health
# curl: (7) Failed to connect to localhost port 5000 -- there's no `ports:` mapping for `api` anymore
```

**Watch the resource limits take effect:**

```bash
docker compose -f docker-compose.prod.yml exec api cat /sys/fs/cgroup/memory.max
# 268435456  (256 * 1024 * 1024 — matches the 256M limit, not the host's total RAM)
```

**Prove `unless-stopped` restart behavior:**

```bash
docker compose -f docker-compose.prod.yml kill api
docker compose -f docker-compose.prod.yml ps    # api is already back up (STATUS: Up ... (healthy))
```

**Tear down:**

```bash
docker compose -f docker-compose.prod.yml down
```

## Key takeaways

- Never expose an app container directly in production — put a reverse proxy in front, and let it
  own the public port(s) and TLS.
- `unless-stopped` is the right default restart policy for long-running services.
- `deploy.resources.limits` protects the whole host from any single misbehaving container, and
  works with plain `docker compose up` in modern Compose — no Swarm required.
- Dev and prod having *separate* compose files (rather than one file trying to serve both) keeps
  each one simple and readable.

## Exercise

Add a second Nginx `location /notes { ... proxy_pass ... }` block with `limit_req` rate limiting
(look up Nginx's `limit_req_zone`), rebuild, and confirm rapid repeated requests start getting
`503`s from Nginx — a basic defense against a client hammering the API, enforced before traffic
ever reaches the app.

## Up next

[20 · Capstone Project](../20-capstone-project) — the finished stack, and where to take it from
here.
