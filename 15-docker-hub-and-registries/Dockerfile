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
CMD ["python", "app.py"]
