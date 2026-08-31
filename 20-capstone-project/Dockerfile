# ---- Stage 1: "builder" ----
FROM python:3.12 AS builder

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# ---- Stage 2: "tester" ----
# Only ever built explicitly with `docker build --target tester`. The final
# `runtime` stage below does NOT depend on this one, so a plain
# `docker build .` never runs it — CI calls it out as its own step instead
# (see .github/workflows/docker-ci.yml).
FROM builder AS tester

COPY requirements-dev.txt .
RUN pip install --no-cache-dir --user -r requirements-dev.txt
COPY . .
RUN python -m pytest tests/ -v

# ---- Stage 3: "runtime" (the image that actually ships) ----
FROM python:3.12-slim

RUN useradd --create-home --uid 1000 appuser
WORKDIR /app

COPY --from=builder /root/.local /home/appuser/.local

# Explicit file list here (instead of `COPY . .`) so tests/, requirements-dev.txt,
# and CI config never end up inside the image that actually ships.
COPY app.py config.py db.py cache.py ./
RUN chown -R appuser:appuser /app
ENV PATH=/home/appuser/.local/bin:$PATH
USER appuser

EXPOSE 5000

HEALTHCHECK --interval=10s --timeout=3s --start-period=5s --retries=3 \
  CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://localhost:5000/health').status == 200 else 1)"

CMD ["python", "app.py"]
