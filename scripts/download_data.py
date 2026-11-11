"""Download the datasets declared in config/sources.yml.

Run it through the course command, not directly:

    ./course data                      every file of every source
    ./course data --source imdb        every file of one source
    ./course data --only title_ratings one dataset, by its short name

Which files exist is not written in this script. It is declared in
config/sources.yml, so adding a file to the pipeline is a change to that file
and nothing else.

Files land in each source's target folder, exactly as the source publishes
them. Running the script again only downloads files that changed on the
server, which it detects by comparing each file's size and last-modified date
with what it recorded last time in a manifest.json next to the files.
"""

from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

import yaml

CONFIG = Path("config/sources.yml")
USER_AGENT = "course-intro-to-data-engineering (educational, non-commercial)"
CHUNK = 1024 * 1024

SOURCE_FIELDS = ("description", "base_url", "target", "terms", "files")
FILE_FIELDS = ("name", "dataset", "description")


class ConfigError(Exception):
    """config/sources.yml is missing something or is malformed."""


def load_sources(path: Path = CONFIG) -> dict:
    """Read and validate the declarations. Fail early, with a useful message."""
    if not path.exists():
        raise ConfigError(f"{path} does not exist")
    try:
        document = yaml.safe_load(path.read_text()) or {}
    except yaml.YAMLError as error:
        raise ConfigError(f"{path} is not valid YAML: {error}") from error

    sources = document.get("sources")
    if not isinstance(sources, dict) or not sources:
        raise ConfigError(f"{path} must have a 'sources' mapping with at least one source")

    datasets_seen: dict[str, str] = {}
    for source_name, source in sources.items():
        if not isinstance(source, dict):
            raise ConfigError(f"source '{source_name}' must be a mapping")
        for field in SOURCE_FIELDS:
            if not source.get(field):
                raise ConfigError(f"source '{source_name}' is missing '{field}'")
        if not source["base_url"].startswith("https://"):
            raise ConfigError(f"source '{source_name}': base_url must start with https://")
        target = Path(source["target"])
        if target.is_absolute() or ".." in target.parts or target.parts[0] != "data":
            raise ConfigError(f"source '{source_name}': target must be a folder under data/")
        if not isinstance(source["files"], list):
            raise ConfigError(f"source '{source_name}': 'files' must be a list")
        for entry in source["files"]:
            if not isinstance(entry, dict):
                raise ConfigError(f"source '{source_name}': each file must be a mapping")
            for field in FILE_FIELDS:
                if not entry.get(field):
                    raise ConfigError(
                        f"source '{source_name}': a file is missing '{field}': {entry}"
                    )
            if "/" in entry["name"] or entry["name"].startswith("."):
                raise ConfigError(
                    f"source '{source_name}': file name must be a plain name: {entry['name']}"
                )
            if entry["dataset"] in datasets_seen:
                raise ConfigError(
                    f"dataset name '{entry['dataset']}' is used twice "
                    f"(in '{datasets_seen[entry['dataset']]}' and '{source_name}')"
                )
            datasets_seen[entry["dataset"]] = source_name
    return sources


def remote_state(url: str) -> dict:
    """Ask the server what it has, without downloading the file."""
    request = urllib.request.Request(url, method="HEAD", headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=60) as response:
        return {
            "size": int(response.headers.get("Content-Length", 0)),
            "last_modified": response.headers.get("Last-Modified", ""),
        }


def is_current(local: Path, remote: dict, recorded: dict | None) -> bool:
    """True when the local copy is the same file the server offers now."""
    if not local.exists() or recorded is None:
        return False
    return recorded == remote and local.stat().st_size == remote["size"]


def download(url: str, destination: Path) -> None:
    """Stream the file to disk. A partial download never replaces a good file."""
    partial = destination.with_name(destination.name + ".part")
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
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
                print(f"  {destination.name}: {done * 100 // total}%", flush=True)
                next_report += 25
    partial.replace(destination)


def main() -> int:
    try:
        sources = load_sources()
    except ConfigError as error:
        print(f"error: {error}", file=sys.stderr)
        return 2

    all_datasets = sorted(
        entry["dataset"] for source in sources.values() for entry in source["files"]
    )
    parser = argparse.ArgumentParser(
        description="Download the datasets declared in config/sources.yml."
    )
    parser.add_argument(
        "--source",
        action="append",
        choices=sorted(sources),
        metavar="SOURCE",
        help="download only this source; may be given more than once",
    )
    parser.add_argument(
        "--only",
        action="append",
        choices=all_datasets,
        metavar="DATASET",
        help="download only this dataset, by its short name; may be given more than once. "
        f"Declared: {', '.join(all_datasets)}",
    )
    args = parser.parse_args()

    downloaded = 0
    skipped = 0
    for source_name, source in sources.items():
        if args.source and source_name not in args.source:
            continue
        wanted = [
            entry for entry in source["files"] if not args.only or entry["dataset"] in args.only
        ]
        if not wanted:
            continue

        target = Path(source["target"])
        target.mkdir(parents=True, exist_ok=True)
        manifest_path = target / "manifest.json"
        manifest = json.loads(manifest_path.read_text()) if manifest_path.exists() else {}

        print(f"Source: {source_name} ({source['description']})")
        print(f"Terms of use: {source['terms']}")
        for entry in wanted:
            name = entry["name"]
            url = source["base_url"].rstrip("/") + "/" + name
            try:
                remote = remote_state(url)
                if is_current(target / name, remote, manifest.get(name)):
                    print(f"up to date  {name}")
                    skipped += 1
                    continue
                print(f"downloading {name} ({remote['size'] / 1024 / 1024:.0f} MB)")
                download(url, target / name)
            except (urllib.error.URLError, TimeoutError, OSError) as error:
                print(f"error: could not download {name}: {error}", file=sys.stderr)
                print(
                    "Check your internet connection and run ./course data again.",
                    file=sys.stderr,
                )
                return 1
            manifest[name] = remote
            manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
            downloaded += 1
        print()

    print(f"Done. Downloaded {downloaded}, already up to date {skipped}.")
    # A fixed last line that checkpoints and CI can read.
    print(f"DOWNLOADED {downloaded}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
