# 14 · Multi-Stage Builds

## Learning objectives

- Write a Dockerfile with more than one `FROM` stage.
- Use `COPY --from=<stage>` to carry forward only what's needed into the final image.
- Measure the size difference multi-stage builds make, for yourself.

## The problem: build tools you don't need at runtime

Some Python packages need compilers/build headers to install. The base `python:3.12` image
includes those tools — but your app never needs them again once installation is done. Shipping
them in your production image is pure waste: bigger image, slower pulls, bigger attack surface.

**Multi-stage builds** solve this: use a "fat" image to *build* things, then copy only the
finished result into a "slim" image that actually ships.

## The Dockerfile

```dockerfile
# ---- Stage 1: "builder" ----
FROM python:3.12 AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# ---- Stage 2: "runtime" ----
FROM python:3.12-slim
WORKDIR /app
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH
COPY . .
EXPOSE 5000
CMD ["python", "app.py"]
```

- `AS builder` names the first stage so we can reference it later.
- `FROM python:3.12-slim` starts a **completely fresh image** — none of the builder stage's layers
  are included automatically.
- `COPY --from=builder /root/.local /root/.local` reaches back into the builder stage and copies
  across *only* the installed packages (`pip install --user` puts them under `~/.local`) — not the
  compilers, not the apt cache, not anything else that made the builder stage big.

## Demo

`Dockerfile.single-stage` is kept in this folder purely so you can compare directly — it's the
same style every previous topic used.

```bash
cd 14-multi-stage-builds

docker build -f Dockerfile.single-stage -t notes-api:single-stage .
docker build -f Dockerfile -t notes-api:multi-stage .

docker images notes-api
```

Compare the `SIZE` column — the multi-stage image is meaningfully smaller, purely because the
compilers and build-time cruft never made it into the final layers.

```bash
# Confirm it still works exactly the same
cp .env.example .env
docker compose up --build -d
curl http://localhost:5000/health
```

(`docker-compose.yml` builds using the default `Dockerfile`, i.e. the multi-stage one.)

## Key takeaways

- `FROM ... AS name` + `COPY --from=name` lets you use a heavyweight image to build, and a
  lightweight image to ship.
- Only what you explicitly `COPY --from=` crosses between stages — everything else in the builder
  stage is left behind.
- Smaller images pull faster, start faster, and simply have less in them that could go wrong or be
  attacked — a theme [17-docker-security-best-practices](../17-docker-security-best-practices)
  builds on directly.

## Exercise

Add a third stage: `FROM builder AS tester` that runs a trivial `RUN python -c "import flask,
psycopg2, redis"` sanity check, and confirm `docker build --target tester .` succeeds while never
producing the final runtime image. This is the same `--target` mechanism real CI pipelines use to
run tests against a build stage before producing the shippable image
(see [18-docker-in-cicd](../18-docker-in-cicd)).

## Up next

[15 · Docker Hub & Registries](../15-docker-hub-and-registries) — tagging this image properly and
pushing it somewhere others can pull it from.
