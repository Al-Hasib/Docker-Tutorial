# Docker Tutorial — YouTube Playlist

A full Docker course, one folder per video. Numbered folders (`01-...`, `02-...`) match the
playlist order — just play them top to bottom.

Every folder contains:

- **`README.md`** — the teaching doc for that video: learning objectives, the concept explained,
  a step-by-step demo with the exact commands to run on screen, a commands cheat-sheet, key
  takeaways, and a small exercise for viewers.
- **Python code**, where the topic calls for it (some early conceptual topics don't need any).

## The running example: Notes API

Starting at [`07-dockerfile-basics`](07-dockerfile-basics), every topic builds on the same small
Python app — a **Notes API** (Flask). Each folder holds the **full, runnable state** of the app
*as of that video* (not a diff), so viewers can `cd` into any folder and run it standalone. Across
the playlist the app grows like this:

| Folder | What gets added |
|---|---|
| 07 | A minimal Flask API, in-memory storage, first `Dockerfile` |
| 08 | Better image-building habits: `.dockerignore`, layer caching, build args, tags |
| 09 | Real persistence with SQLite + a named volume |
| 10 | A second container (a tiny client) talking to the API over a custom Docker network |
| 11 | `docker-compose.yml`; storage moves from SQLite to PostgreSQL |
| 12 | A Redis cache added to the stack (api + db + cache) |
| 13 | Config via environment variables and a `.env` file |
| 14 | A multi-stage `Dockerfile` for a smaller, faster image |
| 15 | Tagging/versioning and pushing the image to Docker Hub |
| 16 | Structured logging, a real `/health` check, `HEALTHCHECK` |
| 17 | Security hardening: non-root user, slim base image, secrets |
| 18 | Tests + a GitHub Actions CI/CD pipeline that builds and pushes the image |
| 19 | A production compose file: Nginx reverse proxy, restart policies, resource limits |
| 20 | Capstone: the finished full stack, tied together with a project write-up |

## Playlist

1. [Introduction to Docker](01-introduction-to-docker)
2. [Why Docker?](02-why-docker)
3. [Docker Architecture](03-docker-architecture)
4. [Installing Docker](04-installing-docker)
5. [Images vs Containers](05-images-vs-containers)
6. [Docker CLI Basics](06-docker-cli-basics)
7. [Dockerfile Basics](07-dockerfile-basics)
8. [Building Custom Images](08-building-custom-images)
9. [Docker Volumes](09-docker-volumes)
10. [Docker Networking](10-docker-networking)
11. [Docker Compose](11-docker-compose)
12. [Multi-Container Apps](12-multi-container-apps)
13. [Environment Variables & Config](13-environment-variables-and-config)
14. [Multi-Stage Builds](14-multi-stage-builds)
15. [Docker Hub & Registries](15-docker-hub-and-registries)
16. [Debugging & Logs](16-debugging-and-logs)
17. [Docker Security Best Practices](17-docker-security-best-practices)
18. [Docker in CI/CD](18-docker-in-cicd)
19. [Production Deployment](19-production-deployment)
20. [Capstone Project](20-capstone-project)

## Prerequisites for viewers

- Docker Desktop (or Docker Engine on Linux) installed — covered in topic 4.
- Basic command-line comfort.
- Basic Python (helpful, not required — the code is kept simple and explained line by line).

## Suggested recording flow per video

1. Open the topic's `README.md` on screen as your script/outline.
2. Follow the "Demo" section commands live in a terminal.
3. Walk through the code changes (if any) in an editor.
4. Wrap with the "Key takeaways" and set up the "Exercise" as homework for viewers.
