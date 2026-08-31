# 02 · Why Docker?

## Learning objectives

- Name the concrete problems Docker solves.
- Reproduce the classic "works on my machine" bug live, then fix it with Docker.
- Explain Docker's advantage over traditional VMs at a high level (deep dive in topic 3).

## The problems Docker solves

**1. "Works on my machine"**
An app that depends on a specific language version, OS package, or library often behaves
differently — or doesn't run at all — on a different machine. Docker freezes the *entire runtime
environment* into the image, so the same image behaves identically everywhere.

**2. Painful environment setup**
Without Docker, onboarding a new teammate means: "install Python 3.11, install Postgres 16,
install Redis, set these 12 environment variables, hope your OS package versions match mine."
With Docker: `docker compose up`.

**3. Dependency conflicts between projects**
Project A needs Python 3.9 and Postgres 12. Project B needs Python 3.12 and Postgres 16. Installed
directly on your machine, that's a nightmare. Each in its own container, it's a non-issue.

**4. Inconsistency between dev, staging, and production**
"It worked in staging" is a common and expensive surprise. If dev, staging, and production all run
the *exact same image*, that class of bug disappears.

**5. Slow, heavy virtual machines**
Before Docker, isolation usually meant full VMs — each with its own OS, gigabytes in size, slow to
boot. Containers share the host's kernel, so they're lightweight (megabytes) and start in
milliseconds. (Full explanation with a diagram in [03-docker-architecture](../03-docker-architecture).)

## Demo

The `demo/` folder has a two-line script that only works on Python 3.11+, because it uses the
`tomllib` standard-library module introduced in that version.

```bash
cd demo

# 1. Try it with whatever Python is installed on the host.
#    If your local Python is older than 3.11, this fails:
python app.py
# ModuleNotFoundError: No module named 'tomllib'   <-- "works on my machine" is not guaranteed!

# 2. Now run the exact same code in Docker, regardless of what's installed locally
docker build -t why-docker-demo .
docker run --rm why-docker-demo
# App name : why-docker-demo
# Version  : 0.1.0
# Author   : Docker Tutorial
```

The Dockerfile pins `python:3.11-slim`, so the container always has a Python new enough for
`tomllib` — no matter what's (or isn't) installed on the host. Every machine that runs this image
gets the identical result.

## Key takeaways

- Docker doesn't just "run apps" — it eliminates a whole category of environment-mismatch bugs.
- The fix isn't "everyone installs Python 3.11" — it's "the image *carries* Python 3.11 with it."
- This is the foundation every later topic builds on: reproducible builds, reproducible deploys.

## Exercise

Change `python:3.11-slim` in the Dockerfile to `python:3.10-slim`, rebuild, and rerun. Watch the
exact same `ModuleNotFoundError` happen *inside* the container — proving it's not "Docker magic,"
it's simply that the image controls the runtime version. Put the tag back to `3.11-slim` afterward.

## Up next

[03 · Docker Architecture](../03-docker-architecture) — what's actually happening under the hood
when you run `docker run`.
