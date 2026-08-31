# ---- Stage 1: "builder" ----
# Uses the FULL python image (has compilers/build tools some packages need
# to install). Its only job is producing installed Python packages.
FROM python:3.12 AS builder

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# ---- Stage 2: "runtime" ----
# Starts a BRAND NEW image from the slim base. None of the builder stage's
# build tools, apt cache, or layers come along for free — we copy across
# only the one thing we actually need: the installed packages.
FROM python:3.12-slim

WORKDIR /app

COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

COPY . .

EXPOSE 5000

# Docker (and docker compose) will periodically run this INSIDE the
# container and mark it unhealthy if it fails --retries times in a row.
# See `docker inspect` / `docker ps` for where this shows up.
HEALTHCHECK --interval=10s --timeout=3s --start-period=5s --retries=3 \
  CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://localhost:5000/health').status == 200 else 1)"

CMD ["python", "app.py"]
