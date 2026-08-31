# Every instruction below creates one cached, read-only image layer.
# See 03-docker-architecture for why that matters.

# 1. Start from an official base image (OS + Python already installed)
FROM python:3.12

# 2. Every instruction after this runs from /app inside the image
WORKDIR /app

# 3. Copy dependency list first (see topic 8 for *why* the order matters)
COPY requirements.txt .

# 4. Install dependencies into the image
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy the rest of the application code in
COPY . .

# 6. Documentation only — does NOT actually publish the port (see docker run -p below)
EXPOSE 5000

# 7. The command that runs when a container starts from this image
CMD ["python", "app.py"]
