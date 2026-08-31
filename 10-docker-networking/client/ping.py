"""A second, separate container that talks to the Notes API over Docker's
network — using the OTHER container's NAME as a hostname.

This only works because both containers are attached to the same
user-defined bridge network, which gives every container automatic DNS
resolution by container name. See the README for the exact `docker network`
commands.
"""
import os
import sys
import time

import requests

# Defaults to "notes-api" — the --name we'll give the API container below.
API_HOST = os.environ.get("API_HOST", "notes-api")
API_URL = f"http://{API_HOST}:5000"

print(f"Client is targeting: {API_URL}")

for attempt in range(5):
    try:
        health = requests.get(f"{API_URL}/health", timeout=2)
        health.raise_for_status()
        print(f"Health check OK: {health.json()}")
        break
    except requests.RequestException as exc:
        print(f"Attempt {attempt + 1}: not reachable yet ({exc})")
        time.sleep(2)
else:
    print("Could not reach the API. Is it on the same Docker network?")
    sys.exit(1)

created = requests.post(f"{API_URL}/notes", json={"text": "Hello from the client container"})
print("Created:", created.json())

notes = requests.get(f"{API_URL}/notes")
print("All notes seen by the client:", notes.json())
