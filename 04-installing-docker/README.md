# 04 · Installing Docker

## Learning objectives

- Install Docker on Windows, macOS, or Linux.
- Verify the install with a real container run.
- Know the difference between Docker Desktop and Docker Engine.

## Docker Desktop vs. Docker Engine

| | Docker Desktop | Docker Engine |
|---|---|---|
| Platforms | Windows, macOS (+ Linux) | Linux only |
| What it is | GUI app + Docker Engine + a lightweight Linux VM (on Win/Mac) | Just the daemon (`dockerd`) + CLI, running natively |
| Typical use | Local development on a laptop | Servers, CI runners, cloud VMs |
| License note | Free for personal use / small business / education; paid tier for larger companies | Free, open source (Apache 2.0) |

Recommendation for viewers: **Docker Desktop** if you're on Windows or macOS and just want to
follow along; native **Docker Engine** if you're on Linux (Desktop also works on Linux but isn't
required there).

## Install steps

**Windows**
1. Enable WSL2 (`wsl --install` in an admin PowerShell, then reboot if prompted).
2. Download and install **Docker Desktop** from docker.com.
3. Launch Docker Desktop and make sure the WSL2 backend is enabled (Settings → General).

**macOS**
1. Download **Docker Desktop** for your chip (Apple Silicon or Intel) from docker.com.
2. Drag it into `Applications` and launch it.

**Linux (Ubuntu/Debian example)**
```bash
# Docker's convenience install script — fine for a demo/dev machine
curl -fsSL https://get.docker.com | sh

# Run docker without sudo (log out/in afterward for this to take effect)
sudo usermod -aG docker $USER
```

## Verify the install

```bash
docker --version
docker compose version
docker run hello-world
```

If `hello-world` prints its friendly message (the same one from topic 1), the install is good.

## Key takeaways

- Docker Desktop = GUI + engine + (on Win/Mac) a hidden Linux VM, aimed at local dev.
- Docker Engine = just the daemon + CLI, the norm on Linux servers.
- `docker run hello-world` is the standard "is my install working?" smoke test — remember it,
  you'll use it after every Docker install for the rest of your life.

## Exercise

Run `docker info` and find three pieces of info about *your* install: the storage driver, the
number of CPUs Docker can see, and the total memory Docker is allowed to use. On Docker Desktop,
compare that memory number to your machine's total RAM — it's usually capped, and adjustable in
Settings → Resources.

## Up next

[05 · Images vs Containers](../05-images-vs-containers) — now that Docker is installed, let's
build and run our own image.
