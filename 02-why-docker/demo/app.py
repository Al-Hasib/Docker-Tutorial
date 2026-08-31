"""Tiny script used to demonstrate the "works on my machine" problem.

`tomllib` is part of the Python standard library ONLY from Python 3.11 onward.
On a machine with an older Python installed, this import fails outright — even
though the code is perfectly correct. Docker fixes this by shipping the exact
Python version the app needs, every time, everywhere.
"""
import tomllib

with open("data.toml", "rb") as f:
    config = tomllib.load(f)

print(f"App name : {config['app']['name']}")
print(f"Version  : {config['app']['version']}")
print(f"Author   : {config['app']['author']}")
