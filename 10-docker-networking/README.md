# 10 · Docker Networking

## Learning objectives

- Explain the default `bridge` network and its main limitation (no automatic DNS by name).
- Create a user-defined bridge network and attach containers to it.
- Get two containers talking to each other by container name.

## The setup

Two containers this time:

- **`notes-api`** — the same v3 API from topic 9 (unchanged: `app.py`, `db.py`, `Dockerfile`).
- **`client/`** — a small standalone script, `ping.py`, that calls the API over HTTP using the
  *container name* `notes-api` as the hostname.

## Docker's network types, briefly

| Network driver | What it is |
|---|---|
| `bridge` (default, unnamed) | Every container gets a private IP; containers **cannot** resolve each other by name, only by IP. This is what you get if you never touch networking. |
| **User-defined `bridge`** | Same isolation, but Docker runs an embedded DNS server on it — containers *can* resolve each other **by container name**. This is the one you actually want for multi-container apps. |
| `host` | Container shares the host's network stack directly — no isolation, rarely what you want. |
| `none` | No networking at all. |

Docker Compose (next topic) creates a user-defined bridge network for you automatically — this
video does it by hand once, so you know exactly what Compose is doing under the hood.

## Demo

```bash
cd 10-docker-networking

# 1. Create a user-defined bridge network
docker network create notes-net

# 2. Build both images
docker build -t notes-api:v3 .
docker build -t notes-client:v1 ./client

# 3. Run the API attached to that network, named "notes-api"
#    (the client will use this exact name to reach it)
docker run -d --name notes-api --network notes-net -p 5000:5000 notes-api:v3

# 4. Run the client on the SAME network
docker run --rm --network notes-net notes-client:v1
```

Expected output from the client: it resolves `notes-api` to the API container's internal IP,
gets a health check, creates a note, and lists all notes — all without ever knowing an IP address.

**Prove name resolution is the network's doing, not magic:**

```bash
docker network inspect notes-net   # see both containers listed, each with an internal IP

# Run the client WITHOUT --network — it's on the default bridge, notes-api is on notes-net
docker run --rm notes-client:v1
# Attempt 1..5: not reachable yet (... Name or service not known ...)
```

Without a shared user-defined network, there's no DNS entry for `notes-api` at all — this is
exactly the failure mode the network solves.

**Inspect the network further:**

```bash
docker network ls
docker network inspect notes-net --format '{{json .Containers}}'
```

**Clean up:**

```bash
docker rm -f notes-api
docker network rm notes-net
```

## Key takeaways

- The default bridge network gives containers IPs but not name-based DNS — a real limitation.
- A user-defined bridge network (`docker network create`) adds automatic DNS: containers reach
  each other by `--name`.
- This is precisely the mechanism Docker Compose automates for you — which is exactly why the
  next video's `docker-compose.yml` needs zero explicit network configuration to make services
  reach each other by name.

## Exercise

Create a second network, attach only the API to it, and confirm (with `docker network inspect`)
that the client — attached solely to `notes-net` — has no path to it. This is the isolation half of
networking: containers not sharing a network genuinely cannot reach each other, which is a
deliberate security boundary, not just a missing feature.

## Up next

[11 · Docker Compose](../11-docker-compose) — replacing all those manual `docker network` /
`docker run` commands with one declarative file.
