# Deliberately pinned to a version new enough for `tomllib` (3.11+),
# guaranteeing this script works the same everywhere — regardless of what
# Python (if any) is installed on the host machine.
FROM python:3.11-slim

WORKDIR /app
COPY . .

CMD ["python", "app.py"]
