# 09 · Docker Volumes

## Learning objectives

- Explain why a container's filesystem is ephemeral by default.
- Persist data across container restarts *and* removal using a named volume.
- Know the difference between a named volume and a bind mount, and when to use each.

## The problem: containers are throwaway

Every container gets its own writable layer (topic 3). Delete the container, and that layer —
along with anything the app wrote to disk — is gone. Topic 7 and 8's Notes API "solved" this by...
not solving it: notes lived in a Python list in RAM, wiped out by every restart.

This video switches storage to SQLite (see `db.py`), a real file on disk at `/app/data/notes.db`.
That's necessary but **not sufficient** — a file written inside the container's writable layer is
just as ephemeral as RAM once the container is removed. The fix is a **volume**: storage that
lives outside any single container's lifecycle, which Docker mounts into the container at a given
path.

## Named volumes vs. bind mounts

| | Named volume | Bind mount |
|---|---|---|
| Managed by | Docker (`docker volume` commands) | You (a specific path on your host) |
| Where it lives | Docker-managed storage area | Any host folder you choose |
| Typical use | Real persistent data (databases, uploads) | Live-syncing source code during development |
| Example flag | `-v notes-data:/app/data` | `-v $(pwd)/data:/app/data` |

We'll use a **named volume** for the database (Docker manages it, works identically on every OS),
and mention a bind mount for local dev at the end.

## Demo

```bash
cd 09-docker-volumes
docker build -t notes-api:v3 .

# Create a named volume explicitly (docker run would auto-create it too, but
# being explicit makes it visible in the demo)
docker volume create notes-data

docker run -d --name notes-api -p 5000:5000 -v notes-data:/app/data notes-api:v3
```

`-v notes-data:/app/data` mounts the volume `notes-data` at `/app/data` **inside** the container —
exactly the path `db.py` writes `notes.db` to.

```bash
curl -X POST http://localhost:5000/notes -H "Content-Type: application/json" -d '{"text":"Survive a restart"}'
curl http://localhost:5000/notes
```

**Prove restart-safety:**

```bash
docker restart notes-api
curl http://localhost:5000/notes   # note is still there
```

**Prove it survives even removing the container** (the real test — the old in-memory version
could never pass this):

```bash
docker rm -f notes-api
docker run -d --name notes-api -p 5000:5000 -v notes-data:/app/data notes-api:v3
curl http://localhost:5000/notes   # still there — the DATA lives in the volume, not the container
```

**Inspect and manage the volume directly:**

```bash
docker volume ls
docker volume inspect notes-data
```

**Clean up (this is the one command that actually deletes the notes for good):**

```bash
docker rm -f notes-api
docker volume rm notes-data
```

## Bind mounts, briefly

For local development, it's common to bind-mount your source code so edits show up without
rebuilding:

```bash
docker run -d --name notes-api -p 5000:5000 -v $(pwd):/app notes-api:v3
```

This overlays your entire current folder onto `/app` in the container — great for live-editing
during development, but not something you'd use for a database file in production (a bind mount
ties you to one specific host path/machine; a named volume doesn't).

## Key takeaways

- Container filesystems are ephemeral by default — data must live in a volume to survive
  `docker rm`.
- A named volume (`-v name:/path`) is Docker-managed and portable; a bind mount (`-v
  /host/path:/path`) ties you to a specific host folder, useful mainly for local dev.
- `docker volume rm` is the command that actually deletes persisted data — treat it with respect.

## Exercise

Run `docker volume inspect notes-data` and find the `Mountpoint` field — the real folder on your
host (or the Docker Desktop VM) where the SQLite file physically lives. On Linux, try browsing to
it with `sudo ls` and find `notes.db` sitting there directly.

## Up next

[10 · Docker Networking](../10-docker-networking) — letting a second container talk to this one.
