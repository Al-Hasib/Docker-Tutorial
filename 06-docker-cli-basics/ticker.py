"""Prints a heartbeat every 2 seconds, forever.

Deliberately long-running (unlike the previous topic's script) so there's
something alive to `docker ps`, `docker logs -f`, `docker exec`, and
`docker stop` against.
"""
import time
from datetime import datetime, timezone

count = 0
while True:
    count += 1
    print(f"[{datetime.now(timezone.utc).isoformat()}] tick #{count}", flush=True)
    time.sleep(2)
