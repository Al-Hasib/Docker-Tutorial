# 07 · Dockerfile Basics

## Learning objectives

- Read and write every basic Dockerfile instruction: `FROM`, `WORKDIR`, `COPY`, `RUN`, `EXPOSE`,
  `CMD`.
- Build an image from a Dockerfile and run it with port mapping.
- Meet the **Notes API** — the app this entire course builds on from here forward.

## Meet the app: Notes API

A small Flask REST API for managing text notes, kept intentionally simple:

| Method | Path | What it does |
|---|---|---|
| `GET` | `/health` | Returns `{"status": "ok"}` — used to check the app is alive |
| `GET` | `/notes` | List all notes |
| `POST` | `/notes` | Create a note — body: `{"text": "..."}` |
| `GET` | `/notes/<id>` | Get one note |
| `DELETE` | `/notes/<id>` | Delete one note |

Storage right now is just a Python list in memory — restart the container and every note is gone.
That's intentional for this video; [09-docker-volumes](../09-docker-volumes) is where we fix it.

## The Dockerfile, instruction by instruction

```dockerfile
FROM python:3.12          # Start from an official image with Python already installed
WORKDIR /app               # Every following instruction runs from /app inside the image
COPY requirements.txt .    # Copy just the dependency list first
RUN pip install --no-cache-dir -r requirements.txt   # Install dependencies (this becomes a cached layer)
COPY . .                   # Now copy the rest of the app code
EXPOSE 5000                 # Documentation: "this container listens on port 5000"
CMD ["python", "app.py"]   # The default command when a container starts
```

Two instructions deserve special attention:

- **`RUN` vs `CMD`** — `RUN` executes *during the build* and its result is baked into the image
  (e.g. installing packages). `CMD` does *not* run during build — it's the command the container
  executes when it *starts*. A Dockerfile can have many `RUN`s but effectively one `CMD`.
- **`EXPOSE` is documentation, not magic** — it doesn't publish the port to your host. You still
  need `-p` on `docker run` to actually reach it, as you'll see below.

## Demo

```bash
cd 07-dockerfile-basics

docker build -t notes-api:v1 .
docker run -d --name notes-api -p 5000:5000 notes-api:v1
```

`-p 5000:5000` maps **host port : container port** — without it, port 5000 stays private inside
the container and you can't reach it from your browser or `curl`.

```bash
curl http://localhost:5000/health
curl http://localhost:5000/notes
curl -X POST http://localhost:5000/notes -H "Content-Type: application/json" -d '{"text":"Learn Docker"}'
curl http://localhost:5000/notes
curl http://localhost:5000/notes/1
curl -X DELETE http://localhost:5000/notes/1
curl http://localhost:5000/notes
```

Now prove storage is *not* persistent yet:

```bash
docker restart notes-api
curl http://localhost:5000/notes   # empty again — the in-memory list reset
```

Clean up:

```bash
docker rm -f notes-api
```

## Key takeaways

- A Dockerfile is a linear recipe; each instruction adds one image layer.
- `RUN` = build-time; `CMD` = the container's runtime command.
- `EXPOSE` documents a port; `-p host:container` on `docker run` is what actually publishes it.
- This app has no persistence yet — by design, to set up the next topic.

## Exercise

Add a new `PATCH /notes/<id>` route that updates a note's `text`, rebuild the image with a new tag
(`notes-api:v1.1`), and test it with `curl -X PATCH ... -d '{"text":"updated"}'`.

## Up next

[08 · Building Custom Images](../08-building-custom-images) — the habits that make builds fast,
small, and reproducible.
