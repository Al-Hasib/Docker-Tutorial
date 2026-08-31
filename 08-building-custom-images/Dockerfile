FROM python:3.12

# Optional build-time metadata — passed with `--build-arg` at build time,
# baked into the image as a label. Doesn't change runtime behavior.
ARG APP_VERSION=dev
LABEL app.version=$APP_VERSION

WORKDIR /app

# Dependency files copied BEFORE the rest of the source on purpose:
# Docker caches each layer and only re-runs a layer (and everything after it)
# if its inputs changed. requirements.txt changes rarely; app.py changes
# often. With this order, editing app.py does NOT invalidate the
# `pip install` layer, so rebuilds after a code-only change are near-instant.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000
CMD ["python", "app.py"]
