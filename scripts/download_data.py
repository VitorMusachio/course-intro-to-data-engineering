"""Download the IMDb datasets used throughout the course.

Run it through the course command, not directly:

    ./course data

The files land in data/imdb/, compressed, exactly as IMDb publishes them.
Running it again only downloads files that changed on IMDb's side, which the
script detects by comparing each file's size and last-modified date with what
it recorded last time in data/imdb/manifest.json.

IMDb licenses this data for personal and non-commercial use. It is never
committed to the repository: see https://developer.imdb.com/non-commercial-datasets/
"""

from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

BASE_URL = "https://datasets.imdbws.com/"
FILES = [
    "name.basics.tsv.gz",
    "title.akas.tsv.gz",
    "title.basics.tsv.gz",
    "title.crew.tsv.gz",
    "title.episode.tsv.gz",
    "title.principals.tsv.gz",
    "title.ratings.tsv.gz",
]
TARGET = Path("data/imdb")
MANIFEST = TARGET / "manifest.json"
USER_AGENT = "course-intro-to-data-engineering (educational, non-commercial)"
CHUNK = 1024 * 1024


def remote_state(name: str) -> dict:
    """Ask the server what it has, without downloading the file."""
    request = urllib.request.Request(
        BASE_URL + name, method="HEAD", headers={"User-Agent": USER_AGENT}
    )
    with urllib.request.urlopen(request, timeout=60) as response:
        return {
            "size": int(response.headers.get("Content-Length", 0)),
            "last_modified": response.headers.get("Last-Modified", ""),
        }


def is_current(name: str, remote: dict, manifest: dict) -> bool:
    """True when the local copy is the same file the server offers now."""
    local = TARGET / name
    if not local.exists() or name not in manifest:
        return False
    return manifest[name] == remote and local.stat().st_size == remote["size"]


def download(name: str) -> None:
    """Stream the file to disk. A partial download never replaces a good file."""
    partial = TARGET / (name + ".part")
    request = urllib.request.Request(BASE_URL + name, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=60) as response, open(partial, "wb") as out:
        total = int(response.headers.get("Content-Length", 0))
        done = 0
        next_report = 0
        while True:
            block = response.read(CHUNK)
            if not block:
                break
            out.write(block)
            done += len(block)
            if total and done * 100 // total >= next_report:
                print(f"  {name}: {done * 100 // total}%", flush=True)
                next_report += 25
    partial.replace(TARGET / name)


def main() -> int:
    parser = argparse.ArgumentParser(description="Download the IMDb datasets.")
    parser.add_argument(
        "--only",
        action="append",
        choices=FILES,
        metavar="FILE",
        help="download only this file; may be given more than once",
    )
    args = parser.parse_args()
    wanted = args.only or FILES

    TARGET.mkdir(parents=True, exist_ok=True)
    manifest = json.loads(MANIFEST.read_text()) if MANIFEST.exists() else {}

    downloaded = 0
    skipped = 0
    for name in wanted:
        try:
            remote = remote_state(name)
            if is_current(name, remote, manifest):
                print(f"up to date  {name}")
                skipped += 1
                continue
            print(f"downloading {name} ({remote['size'] / 1024 / 1024:.0f} MB)")
            download(name)
        except (urllib.error.URLError, TimeoutError, OSError) as error:
            print(f"error: could not download {name}: {error}", file=sys.stderr)
            print("Check your internet connection and run ./course data again.", file=sys.stderr)
            return 1
        manifest[name] = remote
        MANIFEST.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
        downloaded += 1

    print()
    print(f"Done. Downloaded {downloaded}, already up to date {skipped}.")
    print(f"Files are in {TARGET}/")
    # A fixed last line that checkpoints and CI can read.
    print(f"DOWNLOADED {downloaded}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
