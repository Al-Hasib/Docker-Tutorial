# 18 · Docker in CI/CD

## Learning objectives

- Write tests that don't require a live database, using an application-testability pattern.
- Add a dedicated "tester" build stage that fails the build if tests fail.
- Wire a GitHub Actions pipeline: test → build → (on `main`) push.

## What changed in the app

`db.init_db()` and `app.run()` now only happen inside `if __name__ == "__main__":`, instead of
running the moment `app.py` is imported. That one change is what makes the app testable: pytest
can `import app` and use Flask's test client without ever touching a real Postgres/Redis.

`tests/test_app.py` exercises the routes with lightweight fakes standing in for `db.get_connection`
and the `cache` module (via `monkeypatch`) — fast, no external services, and still testing the
real route logic in `app.py`.

```bash
cd 18-docker-in-cicd
pip install -r requirements.txt -r requirements-dev.txt
python -m pytest tests/ -v
```

## A dedicated "tester" build stage

```dockerfile
FROM builder AS tester
COPY requirements-dev.txt .
RUN pip install --no-cache-dir --user -r requirements-dev.txt
COPY . .
RUN python -m pytest tests/ -v
```

`RUN python -m pytest tests/ -v` inside a Dockerfile is the key idea: if any test fails, that `RUN`
exits non-zero, which makes the whole `docker build` fail. Tests become a **build step**, not a
separate thing that might get skipped.

The final `runtime` stage does **not** build on top of `tester` — it builds from `builder`
directly, and copies only `app.py config.py db.py cache.py` in explicitly (no `tests/`, no
`requirements-dev.txt`). So:

```bash
docker build -t notes-api .                      # skips tester entirely — fast, ships nothing test-related
docker build --target tester -t notes-api:test . # runs ONLY the tester stage
```

CI calls the second form as its own step, on purpose — see below.

## The pipeline: `.github/workflows/docker-ci.yml`

> Kept inside this topic folder for the course, but GitHub Actions only reads workflows from
> `.github/workflows/` at your **repository root** — in a real project this file lives there, not
> nested in a subfolder.

```yaml
- name: Run tests (tester build stage)
  run: docker build --target tester -t notes-api:test .

- name: Build the runtime image
  run: docker build -t notes-api:${{ github.sha }} .

- name: Log in to Docker Hub
  if: github.ref == 'refs/heads/main'
  uses: docker/login-action@v3
  with:
    username: ${{ secrets.DOCKERHUB_USERNAME }}
    password: ${{ secrets.DOCKERHUB_TOKEN }}

- name: Tag and push
  if: github.ref == 'refs/heads/main'
  run: |
    docker tag notes-api:${{ github.sha }} .../notes-api:${{ github.sha }}
    docker push .../notes-api:${{ github.sha }}
```

Three ideas tying earlier topics together:

- **Tests gate everything else.** The build-image and push steps only run if the tests step
  (`docker build --target tester`) succeeded — that's just normal CI job step ordering, but it's
  the multi-stage Dockerfile that makes "run the tests" expressible as a single `docker build`.
  call.
- **Tagging with the commit SHA** (`github.sha`) instead of a hand-picked version — every build is
  traceable to the exact commit that produced it, an alternative to topic 15's manual
  `VERSION`-file scheme that fits CI better since it needs no human to remember to bump anything.
- **Secrets stay in GitHub Actions secrets**, injected as environment variables at run time — never
  written into the Dockerfile or the image, exactly the rule from topic 17.
- **`if: github.ref == 'refs/heads/main'`** — pull requests get tested and built (catching
  breakage early) but never pushed; only merges to `main` publish a new image.

## Demo (running it locally, the way CI would)

```bash
cd 18-docker-in-cicd

docker build --target tester -t notes-api:test .   # tests run as part of this build
docker build -t notes-api:local .                   # only reached if the above succeeded
```

Break a test on purpose (e.g. change `assert resp.status_code == 400` to `== 999` in
`tests/test_app.py`) and rerun `docker build --target tester -t notes-api:test .` — watch the build
fail with the pytest output. Revert the change afterward.

## Key takeaways

- Guarding side effects (`init_db()`, `app.run()`) behind `if __name__ == "__main__":` is what
  makes a Flask app importable and testable in the first place.
- A "tester" build stage turns `pytest` into something `docker build` itself enforces, not an
  optional extra step someone can forget to run.
- CI secrets (registry credentials) are supplied by the CI platform at run time — the same
  principle as `.env` locally, just a different mechanism.

## Exercise

Add a test for the `/health` endpoint that monkeypatches `cache.get_client` to return an object
whose `.ping()` raises, and assert the response is `503` with `"cache": false` — confirming the
degraded-health behavior from topic 16 is actually covered by a test, not just a demo.

## Up next

[19 · Production Deployment](../19-production-deployment) — running this whole stack the way it'd
actually be deployed.
