# 15 · Docker Hub & Registries

## Learning objectives

- Understand image naming: `[registry/]namespace/repository:tag`.
- Log in, tag, and push an image to Docker Hub; pull it back down elsewhere.
- Know why relying on the `latest` tag for anything real is a bad idea, and what to do instead.

## Anatomy of an image name

```
docker.io / your-username / notes-api : 1.0.0
   |             |             |         |
registry     namespace    repository    tag
(default:
 Docker Hub,
 can be omitted)
```

- No registry prefix (`notes-api:1.0.0`) → assumed to be Docker Hub.
- Other registries are named explicitly: `ghcr.io/you/notes-api:1.0.0` (GitHub Container
  Registry), `<account>.dkr.ecr.<region>.amazonaws.com/notes-api:1.0.0` (AWS ECR), etc. Everything
  in this video works the same way against any of them — only the registry hostname changes.

## Semantic versioning, briefly

This folder has a `VERSION` file (`1.0.0`) as the single source of truth for the app's version.
`MAJOR.MINOR.PATCH`: bump `PATCH` for a bug fix, `MINOR` for a backwards-compatible new feature,
`MAJOR` for a breaking change. Tagging images with a real version — not just `latest` — means you
can always tell exactly what's running, and roll back to a specific one.

## Demo

```bash
cd 15-docker-hub-and-registries

# One-time: log in (prompts for your Docker Hub username/password or token)
docker login
```

`scripts/release.py` wraps the build → tag → push sequence so it's one repeatable command instead
of several to type correctly by hand:

```bash
python scripts/release.py <your-docker-hub-username>
```

Under the hood, that script runs:

```bash
docker build -t notes-api:1.0.0 .
docker tag notes-api:1.0.0 <you>/notes-api:1.0.0
docker tag notes-api:1.0.0 <you>/notes-api:latest
docker push <you>/notes-api:1.0.0
docker push <you>/notes-api:latest
```

`docker tag` doesn't duplicate anything on disk — it just adds another name pointing at the same
image ID. That's why an image can have several tags at once.

**Pull it back down** (simulating a teammate, or a different machine):

```bash
docker rmi <you>/notes-api:1.0.0 <you>/notes-api:latest   # pretend we don't have it locally
docker pull <you>/notes-api:1.0.0
docker run --rm -p 5000:5000 <you>/notes-api:1.0.0
```

## Why not just always use `latest`?

`latest` is a completely ordinary, mutable tag — it means "whatever was last pushed as `latest`,"
nothing more. Two real risks:

1. **No rollback target.** If `latest` breaks in production, you have no easy way to say "give me
   the one before this."
2. **Non-reproducible deploys.** Two people pulling `latest` on different days can get two
   different images without realizing it.

Convention: push a real version tag (`1.0.0`) for anything that matters, and treat `latest` as a
convenience alias at best — many production setups don't even push a `latest` tag at all.

## Key takeaways

- Image names follow `[registry/]namespace/repository:tag` — omitting the registry defaults to
  Docker Hub.
- `docker tag` is cheap — it's a new name for an existing image, not a copy.
- Real version tags are how you get reproducible deploys and a rollback path; `latest` gives you
  neither.

## Exercise

Push a second version (`1.0.1`) after making a trivial change to `app.py`, then use
`docker pull <you>/notes-api:1.0.0` explicitly and confirm (via `curl` and a quick code read) it's
still the *old* behavior — proving specific version tags genuinely protect you from a
"whatever's latest today" surprise.

## Up next

[16 · Debugging & Logs](../16-debugging-and-logs) — properly observing a container once it's
running somewhere you can't just watch a terminal.
