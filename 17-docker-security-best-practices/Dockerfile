# ---- Stage 1: "builder" ----
FROM python:3.12 AS builder

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# ---- Stage 2: "runtime" ----
FROM python:3.12-slim

# Dedicated, unprivileged user. Without this, the process inside the
# container runs as root by default — if the app is ever compromised, an
# attacker gets root INSIDE the container, which is a much better starting
# position for them than an unprivileged user.
RUN useradd --create-home --uid 1000 appuser

WORKDIR /app

COPY --from=builder /root/.local /home/appuser/.local
COPY . .

# Give the app's own user ownership of its files, then switch to it for
# every instruction (and the running container) from here on.
RUN chown -R appuser:appuser /app
ENV PATH=/home/appuser/.local/bin:$PATH
USER appuser

EXPOSE 5000

HEALTHCHECK --interval=10s --timeout=3s --start-period=5s --retries=3 \
  CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://localhost:5000/health').status == 200 else 1)"

CMD ["python", "app.py"]
