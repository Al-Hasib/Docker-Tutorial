# 08 · Building Custom Images

## Learning objectives

- Order Dockerfile instructions to get fast, cached rebuilds.
- Use `.dockerignore` to keep the build context small and clean.
- Tag images meaningfully and pass build-time metadata with `--build-arg`.
- Read `docker image history` to see exactly what each layer cost.

## Same app, better build habits

The Notes API code is unchanged from topic 7 — this video is entirely about *how* we build the
image, not the app itself.

## 1. Layer order = cache efficiency

```dockerfile
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
```

Docker caches each layer. If a layer's inputs haven't changed since the last build, Docker reuses
the cached result instead of re-running it. `requirements.txt` changes rarely; `app.py` changes on
every edit. By copying `requirements.txt` first and installing dependencies *before* copying the
rest of the code, editing `app.py` never invalidates the (slow) `pip install` layer.

**Prove it:**

```bash
cd 08-building-custom-images

# First build — everything runs fresh
docker build -t notes-api:v2 .

# Touch only the app code, then rebuild
echo "# comment" >> app.py
docker build -t notes-api:v2 .
```

Watch the output: `pip install` shows `CACHED`, and the whole rebuild finishes in under a second.
Now revert your test edit:

```bash
git checkout -- app.py   # or just delete the added comment line manually
```

Then try flipping the order (`COPY . .` before installing requirements) as a quick thought
experiment — any code change would now bust the cache and force a full reinstall every time.

## 2. `.dockerignore` — keep the build context lean

When you run `docker build`, Docker first sends everything in the current folder (the "build
context") to the daemon. Without a `.dockerignore`, that includes `.git/`, virtual envs, caches —
none of which belong in the image. Check `.dockerignore` in this folder; it excludes exactly that.

```bash
# See the effect: how many files actually get sent as the build context
DOCKER_BUILDKIT=1 docker build --progress=plain -t notes-api:v2 . 2>&1 | grep "transferring context"
```

## 3. Tagging and build-time metadata

```bash
# Tag with a real version instead of relying on the default "latest"
docker build --build-arg APP_VERSION=2.0.0 -t notes-api:2.0.0 -t notes-api:latest .
```

`--build-arg` passes a value into the `ARG APP_VERSION=dev` in the Dockerfile, which we bake into
an image `LABEL`. Confirm it landed:

```bash
docker inspect notes-api:2.0.0 --format '{{ index .Config.Labels "app.version" }}'
```

`-t notes-api:2.0.0 -t notes-api:latest` — you can apply more than one tag to the same build.
`latest` is just a tag, not "the newest image" — it only means whatever image you last tagged
`latest`, so don't rely on it for anything that matters in production (more in
[15-docker-hub-and-registries](../15-docker-hub-and-registries)).

## 4. Inspecting what each layer cost

```bash
docker image history notes-api:2.0.0
docker images notes-api      # compare sizes across your tags
```

## Key takeaways

- Order matters: put things that change *less often* earlier in the Dockerfile.
- `.dockerignore` isn't optional hygiene — it directly affects build speed and image contents.
- Meaningful tags (`2.0.0`) beat relying on the mutable `latest` tag.
- `docker image history` turns "why is this image so big" from a guess into a measurement.

## Exercise

Add a deliberately large, unnecessary file to this folder (e.g. `dd if=/dev/zero of=junk.bin
bs=1M count=50` on Linux/macOS, or just create any 50MB file on Windows), rebuild without a
`.dockerignore` entry for it, check the image size, then add `junk.bin` to `.dockerignore`,
rebuild, and compare sizes. Delete `junk.bin` afterward.

## Up next

[09 · Docker Volumes](../09-docker-volumes) — giving the Notes API real, restart-proof storage.
