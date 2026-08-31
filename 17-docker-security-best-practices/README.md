# 17 · Docker Security Best Practices

## Learning objectives

- Run a container as a non-root user.
- Reduce a container's runtime privileges: read-only filesystem, dropped capabilities,
  no-new-privileges.
- Know how to scan an image for known vulnerabilities.
- Recap where secrets belong (and don't) across everything the course has covered so far.

## 1. Don't run as root

Every Dockerfile so far has had an implicit problem: without a `USER` instruction, the container's
process runs as **root**. If the app is ever compromised (a bad dependency, an injection bug), the
attacker's starting point is root *inside* the container — a meaningfully worse position than an
unprivileged user, especially combined with any container escape.

```dockerfile
RUN useradd --create-home --uid 1000 appuser
...
RUN chown -R appuser:appuser /app
USER appuser
```

**Verify it:**

```bash
cd 17-docker-security-best-practices
cp .env.example .env
docker compose up --build -d

docker compose exec api whoami
# appuser   (not root)
```

## 2. Shrink the blast radius at the Compose level

```yaml
read_only: true
tmpfs:
  - /tmp
cap_drop:
  - ALL
security_opt:
  - no-new-privileges:true
```

- **`read_only: true`** — the container's filesystem (other than explicit volumes/tmpfs) can't be
  written to at all, even by a compromised process. `tmpfs: [/tmp]` gives back just a small
  in-memory scratch space, in case any library the app uses wants to write temp files.
- **`cap_drop: [ALL]`** — Linux capabilities are fine-grained permissions (bind low ports, change
  file ownership, trace processes, ...). This app needs none of them, so we drop every one instead
  of trusting the (large) default set Docker grants.
- **`no-new-privileges:true`** — blocks any process in the container from gaining *more*
  privileges than it started with (e.g. via a setuid binary), even if something inside is
  exploited.

**Verify the filesystem is actually read-only:**

```bash
docker compose exec api touch /app/should-fail
# touch: cannot touch '/app/should-fail': Read-only file system
```

## 3. Scan the image for known vulnerabilities

```bash
docker build -t notes-api:hardened .

# Docker Desktop ships this built in:
docker scout cves notes-api:hardened

# Or, registry-agnostic:
# docker run --rm -v /var/run/docker.sock:/var/run/docker.sock aquasec/trivy image notes-api:hardened
```

Either tool lists known CVEs by severity for every package in the image — including the base image
itself. A smaller image (topic 14's multi-stage build) has less surface here almost by definition.

## 4. Secrets — the full recap

Across the course:

- **Never bake secrets into a Dockerfile or image layer** (`ENV PASSWORD=...` in a Dockerfile puts
  the value in `docker history` forever, even if a later layer "overwrites" it).
- Local dev: `.env`, gitignored, loaded via `env_file:` (topic 13).
- Anything beyond local dev: a real secrets manager (Docker Swarm secrets, Kubernetes Secrets, or a
  cloud provider's secrets manager) injected at runtime — out of scope for this course, but the
  principle carries over directly: secrets are supplied to the running container, never stored in
  the image.

## 5. Dependency pinning

Every `requirements.txt` in this course has pinned exact versions (`flask==3.0.3`, not
`flask`). An unpinned dependency can silently pull in a new, different, possibly vulnerable version
on every rebuild — pinning makes builds reproducible and vulnerability scanning meaningful (you
know exactly what version is being scanned).

## Key takeaways

- Root-in-container is the security default almost every beginner Dockerfile has — one `USER`
  instruction fixes it.
- `read_only`, `cap_drop: [ALL]`, and `no-new-privileges` cost nothing at runtime for an app that
  doesn't need those privileges, and meaningfully limit what a compromise can do.
- Scan images (`docker scout` / `trivy`) the same way you'd run a linter — regularly, not once.
- Secrets live in the environment at runtime, never in an image layer.

## Exercise

Try adding `cap_add: [NET_ADMIN]` temporarily to see the difference `cap_drop: [ALL]` makes versus
Docker's default capability set — then remove it again, since this app has no legitimate need for
that capability.

## Up next

[18 · Docker in CI/CD](../18-docker-in-cicd) — automating build, test, and push on every commit.
