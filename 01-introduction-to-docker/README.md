# 01 · Introduction to Docker

## Learning objectives

By the end of this video, viewers should be able to:

- Explain, in one sentence, what Docker is.
- Define the core vocabulary: image, container, Dockerfile, registry, Docker Hub, Docker Engine.
- Run their first container.

## What is Docker?

Docker is a platform for **packaging an application together with everything it needs to run**
(code, runtime, system libraries, settings) into a single unit called a **container**, so that it
runs the same way on any machine — your laptop, a teammate's laptop, or a server in the cloud.

Think of it as a shipping container for software: it doesn't matter what's inside or what ship
carries it — the container has a standard shape, so every crane, truck, and ship can handle it the
same way. Docker does the same for software: it doesn't matter what's inside (Python, Node,
databases, ...) — every machine with Docker installed can run it the same way.

## Core vocabulary

| Term | Meaning |
|---|---|
| **Image** | A read-only template/blueprint for a container — your app + its dependencies, frozen at a point in time. |
| **Container** | A running (or stopped) *instance* of an image — an isolated process on your machine. |
| **Dockerfile** | A text file with instructions for building an image. |
| **Docker Engine** | The background service that builds images and runs containers. |
| **Registry** | A server that stores images (e.g. Docker Hub). `docker pull` downloads from one, `docker push` uploads to one. |
| **Docker Hub** | The default public registry, free to use for public images. |

We'll use every one of these terms for the rest of the course — nail them now and everything
else gets easier.

## Demo

No code needed yet — just Docker itself.

```bash
# Confirm Docker is installed and see client/server versions
docker version

# See a system-wide summary: containers, images, storage driver, etc.
docker info

# Run your very first container
docker run hello-world
```

Walk through the `hello-world` output line by line — it literally tells you what Docker just did:

1. The Docker client contacted the Docker daemon.
2. The daemon looked for the `hello-world` image locally and didn't find it.
3. The daemon pulled the image from Docker Hub.
4. The daemon created a new container from that image and ran it.
5. The daemon streamed the output to the client.

That five-step flow *is* Docker in a nutshell, and we'll unpack every step of it across the next
few videos.

## Key takeaways

- Docker packages an app + its dependencies into a portable, isolated unit: a **container**.
- A **container** is a running instance of an **image**.
- `docker run hello-world` just demonstrated the full pull → create → start → output flow.

## Exercise

Run `docker run hello-world` again and use `docker ps -a` to see the *stopped* container it left
behind. Then run `docker images` and find the `hello-world` image sitting locally. Notice the
image stayed even though the container exited — that distinction (image vs container) is exactly
what [05-images-vs-containers](../05-images-vs-containers) digs into.

## Up next

[02 · Why Docker?](../02-why-docker) — the problems Docker actually solves, and why it caught on.
