"""Prints identifying info about the process it's running in.

Run this same image as multiple containers and compare the output — every
container gets its own hostname and its own process list, even though they
all came from the exact same image.
"""
import os
import socket
import time

print(f"Hostname     : {socket.gethostname()}")
print(f"Process PID  : {os.getpid()}")
print(f"Container up : {time.ctime()}")
