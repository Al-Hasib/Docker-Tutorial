"""Build, tag, and push the Notes API image using the version in VERSION.

This is just a thin, readable wrapper around plain `docker` commands — it
exists so the tag/push steps are one repeatable command instead of a few
hand-typed ones you have to remember correctly every time.

Usage:
    python scripts/release.py <docker-hub-username>
"""
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
VERSION = (ROOT / "VERSION").read_text().strip()
IMAGE_NAME = "notes-api"


def run(cmd: list[str]) -> None:
    print(f"$ {' '.join(cmd)}")
    subprocess.run(cmd, check=True, cwd=ROOT)


def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: python scripts/release.py <docker-hub-username>")
        sys.exit(1)

    username = sys.argv[1]
    local_tag = f"{IMAGE_NAME}:{VERSION}"
    remote_versioned = f"{username}/{IMAGE_NAME}:{VERSION}"
    remote_latest = f"{username}/{IMAGE_NAME}:latest"

    run(["docker", "build", "-t", local_tag, "."])
    run(["docker", "tag", local_tag, remote_versioned])
    run(["docker", "tag", local_tag, remote_latest])
    run(["docker", "push", remote_versioned])
    run(["docker", "push", remote_latest])

    print(f"\nPushed {remote_versioned} and {remote_latest}")


if __name__ == "__main__":
    main()
