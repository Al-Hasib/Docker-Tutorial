# 06 · Docker CLI Basics

## Learning objectives

Comfortably run, inspect, debug, and clean up containers using the everyday CLI commands.

## The app

`ticker.py` just prints a timestamped heartbeat every 2 seconds forever — a long-running process
gives us something real to `docker logs`, `docker exec`, and `docker stop` against.

## Demo — the commands, in the order you'd actually use them

```bash
cd 06-docker-cli-basics
docker build -t ticker-demo .
```

**Run it in the foreground first**, so you see the connection between your terminal and the
container directly:

```bash
docker run --name ticker ticker-demo
# Ctrl+C to stop watching (this also stops the container, since it's in the foreground)
docker rm ticker
```

**Now run it detached** (`-d`), the way you'd run any real service:

```bash
docker run -d --name ticker ticker-demo
docker ps                          # see it running, note the CONTAINER ID
```

**Logs** — the container isn't attached to your terminal anymore, so this is how you see its output:

```bash
docker logs ticker                 # dump everything printed so far
docker logs -f ticker              # follow, like `tail -f`  (Ctrl+C to stop following — container keeps running)
docker logs --tail 5 ticker        # just the last 5 lines
```

**Exec** — run an extra command *inside* an already-running container, e.g. to poke around:

```bash
docker exec ticker ls /app
docker exec -it ticker /bin/bash   # interactive shell inside the container
# inside: ps aux; cat ticker.py; exit
```

**Inspect** — the full JSON config Docker holds for the container (IP address, mounts, env, etc.):

```bash
docker inspect ticker
docker inspect -f '{{.State.Status}}' ticker   # pull out just one field
```

**Copy files** between host and container:

```bash
docker cp ticker:/app/ticker.py ./copied-ticker.py
rm copied-ticker.py
```

**Lifecycle** — stop, start, restart, remove:

```bash
docker stop ticker      # sends SIGTERM, container exits
docker start ticker     # starts the SAME container again (state/name preserved)
docker restart ticker   # stop + start in one command
docker stop ticker
docker rm ticker         # remove the (stopped) container entirely
```

**Cleanup**:

```bash
docker images                 # list images
docker rmi ticker-demo         # remove the image
docker system prune            # reclaim space from stopped containers, dangling images, etc.
```

## Cheat sheet

| Command | What it does |
|---|---|
| `docker run [-d] [--name x] IMAGE` | Create + start a container from an image |
| `docker ps` / `docker ps -a` | List running / all containers |
| `docker logs [-f] NAME` | View a container's stdout/stderr |
| `docker exec [-it] NAME CMD` | Run a command inside a running container |
| `docker stop` / `start` / `restart` | Control a container's lifecycle |
| `docker rm NAME` | Delete a stopped container |
| `docker images` / `docker rmi` | List / delete images |
| `docker inspect NAME` | Full JSON detail on a container or image |
| `docker cp SRC DST` | Copy files host ⇄ container |
| `docker system prune` | Clean up unused containers/images/networks |

## Key takeaways

- `-d` (detached) is how you run anything long-lived; `docker logs` is then your window into it.
- `docker exec` lets you run *additional* commands in an already-running container — it does not
  start a new container.
- Stopping a container doesn't delete it — `docker start` brings the very same container back.

## Exercise

Start two `ticker` containers with different names (`ticker-a`, `ticker-b`), then use
`docker stats` (no args) to watch their live CPU/memory usage side by side. `Ctrl+C` to exit, then
clean both up.

## Up next

[07 · Dockerfile Basics](../07-dockerfile-basics) — writing your own Dockerfile from scratch, and
meeting the app we'll build on for the rest of the course.
