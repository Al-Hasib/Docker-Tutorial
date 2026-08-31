# 05 · Images vs Containers

## Learning objectives

- State the difference between an image and a container in one sentence each.
- Prove, hands-on, that many containers can be created from one image.
- Understand why removing a container doesn't affect the image, and vice versa.

## The one-sentence version

- An **image** is a frozen, read-only template — think "class."
- A **container** is a running (or stopped) instance created from that template — think "object."

You can create as many containers from one image as you want; they all start identical and then
immediately diverge, because each one gets its own writable layer, its own process, its own
network namespace.

## Demo

```bash
cd 05-images-vs-containers

# Build ONE image
docker build -t whoami-demo .

# Create THREE separate containers from that same image
docker run --name c1 whoami-demo
docker run --name c2 whoami-demo
docker run --name c3 whoami-demo
```

Look at the output: same image, but each run printed a **different hostname** and a **different
PID** — proof each is its own isolated container, not a shared process.

```bash
# The image is still just ONE thing on disk
docker images whoami-demo

# But there are now THREE containers (all exited, since the script finishes immediately)
docker ps -a --filter ancestor=whoami-demo
```

Now delete a container and confirm the image is untouched:

```bash
docker rm c1
docker images whoami-demo    # still there — the image doesn't depend on any container
```

And delete the image only after all its containers are gone:

```bash
docker rm c2 c3
docker rmi whoami-demo
```

## Key takeaways

- One image → many independent containers. Building doesn't run anything; running doesn't rebuild
  anything.
- Containers are cheap and disposable; images are the durable artifact you version and share.
- `docker ps -a` shows containers (running *and* stopped); `docker images` shows images. Mixing
  these two up is the #1 beginner confusion — you now know better.

## Exercise

Run a fourth container but override its name and have it print something extra:
`docker run --name c4 -e GREETING=hi whoami-demo`. Notice the image never changes — you're just
configuring how a *container* starts, which is exactly what the next video's CLI flags are about.

## Up next

[06 · Docker CLI Basics](../06-docker-cli-basics) — the everyday commands for managing containers.
