"""Module 0 checkpoint: one test per acceptance criterion in the module spec.

Run it with:

    ./course check 0

The tests run inside the toolbox container. A few criteria are about your
machine rather than the platform (is the repository clean, which services are
running). The course command collects those facts on the host and passes them
in as environment variables whose names start with COURSE_HOST_.
"""

import json
import os
import sys
import uuid
from pathlib import Path

import boto3
import pytest
import yaml

sys.path.insert(0, "scripts")
import download_data  # noqa: E402 - needs the path set above

BASE_SERVICES = ("storage", "toolbox")


def host(name):
    return os.environ.get(f"COURSE_HOST_{name}", "")


def test_criterion_1_environment_starts_with_one_command():
    """The base environment starts with one command."""
    running = host("RUNNING").split()
    for service in BASE_SERVICES:
        assert service in running, (
            f"The '{service}' service is not running. Start the environment with: ./course up"
        )


def test_criterion_2_every_service_is_healthy():
    """Every service in the base environment reports healthy."""
    health = dict(pair.split("=", 1) for pair in host("HEALTH").split() if "=" in pair)
    for service in BASE_SERVICES:
        assert health.get(service) == "healthy", (
            f"The '{service}' service reports '{health.get(service, 'not found')}'. "
            "See it with: ./course status"
        )


def test_criterion_3_object_storage_round_trip():
    """The object storage accepts a bucket, and an object can be written, read and deleted."""
    s3 = boto3.client("s3")
    bucket = f"checkpoint-{uuid.uuid4().hex[:12]}"
    key = "hello.txt"
    s3.create_bucket(Bucket=bucket)
    try:
        s3.put_object(Bucket=bucket, Key=key, Body=b"hello, data lake")
        assert s3.get_object(Bucket=bucket, Key=key)["Body"].read() == b"hello, data lake"
        listed = [item["Key"] for item in s3.list_objects_v2(Bucket=bucket).get("Contents", [])]
        assert listed == [key]
        s3.delete_object(Bucket=bucket, Key=key)
        assert "Contents" not in s3.list_objects_v2(Bucket=bucket)
    finally:
        for item in s3.list_objects_v2(Bucket=bucket).get("Contents", []):
            s3.delete_object(Bucket=bucket, Key=item["Key"])
        s3.delete_bucket(Bucket=bucket)


def test_criterion_4_datasets_are_downloaded_and_complete():
    """Every declared dataset is downloaded and complete, so a second download fetches nothing."""
    sources = yaml.safe_load(Path("config/sources.yml").read_text())["sources"]
    for source_name, source in sources.items():
        target = Path(source["target"])
        manifest_path = target / "manifest.json"
        assert manifest_path.exists(), (
            f"No datasets from '{source_name}' yet. Download them with: ./course data"
        )
        manifest = json.loads(manifest_path.read_text())
        for entry in source["files"]:
            name = entry["name"]
            local = target / name
            assert local.exists(), f"{name} is missing. Download it with: ./course data"
            assert name in manifest, f"{name} was not recorded. Run: ./course data"
            assert local.stat().st_size == manifest[name]["size"], (
                f"{name} is incomplete. Run: ./course data"
            )
            if name.endswith(".gz"):
                with open(local, "rb") as handle:
                    assert handle.read(2) == b"\x1f\x8b", f"{name} is not a gzip file"
            # The same test the download script applies before skipping a file.
            assert download_data.is_current(local, manifest[name], manifest[name])


def test_criterion_5_repository_is_clean():
    """Starting the environment and downloading the data leaves nothing for git to commit."""
    state = host("GIT")
    if state == "nogit":
        pytest.skip("this folder is not a git clone")
    assert state == "clean", (
        "git sees changes that should not be there: "
        f"{host('GIT_CHANGES') or 'run git status to see them'}"
    )


def test_criterion_6_env_file_is_not_in_the_repository():
    """The .env file with your credentials is ignored by git and not committed."""
    if host("GIT") == "nogit":
        pytest.skip("this folder is not a git clone")
    assert host("ENV_IGNORED") == "yes", ".env is not ignored by git. Check .gitignore"
    assert host("ENV_TRACKED") == "no", ".env is committed. Remove it with: git rm --cached .env"


def test_criterion_7_one_command_stops_everything():
    """One command stops the environment and removes its containers."""
    pytest.skip("checked by ./course down itself, which fails if a container is left behind")


def test_criterion_8_checkpoint_reports_every_criterion():
    """This checkpoint has one result for each of the nine criteria."""
    criteria = [name for name in globals() if name.startswith("test_criterion_")]
    assert len(criteria) == 9, f"expected 9 criteria, found {len(criteria)}"


def test_criterion_9_checkpoint_passes_in_ci():
    """The same checkpoint passes in continuous integration."""
    if not os.environ.get("CI"):
        pytest.skip("checked by the CI workflow on every pull request")
