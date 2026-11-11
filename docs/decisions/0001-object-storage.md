# 0001. Local object storage

Status: accepted
Date: 2026-11-11

## Context

The course needs an S3-compatible object storage that runs on a learner's laptop in Docker. It holds the data lake from module 2 onward, so Spark, Iceberg and Trino must all work against it.

MinIO was the usual choice for this. Its community edition stopped publishing Docker images in October 2025 and its repository was archived in 2026, so the course cannot build on it.

Three maintained, open-source candidates were tested: SeaweedFS, Garage and RustFS.

## Options

Each candidate went through the same steps in GitHub Actions (`experiments/object-storage/`, workflow "Experiments"). The engines were Spark 4.0.1 with Iceberg 1.10.1, an Iceberg REST catalog, and Trino 480, all with their default S3 client settings.

| Step | SeaweedFS 4.53 | Garage 2.3.0 | RustFS 1.0.0 |
| --- | --- | --- | --- |
| Starts and answers an S3 call | pass | pass | pass |
| S3 round trip (bucket, write, read, list, delete) | pass | pass | pass |
| Spark reads and writes Parquet through `s3a` | pass | pass | pass |
| Spark creates an Iceberg table and appends to it | pass | **fail** | pass |
| Spark reads an earlier Iceberg snapshot | pass | **fail** | pass |
| Trino reads the Iceberg table | pass | **fail** | pass |
| Trino writes an Iceberg table | pass | **fail** | pass |

| Measurement | SeaweedFS 4.53 | Garage 2.3.0 | RustFS 1.0.0 |
| --- | --- | --- | --- |
| Image size | 268 MB | 27 MB | 104 MB |
| Time until the first S3 call succeeds | 9 to 13 s | 4 to 5 s | 7 to 8 s |
| Memory after the test, one sample per run | 79 to 89 MiB | 5 to 6 MiB | 33 to 108 MiB |
| Setup needed before first use | A credentials file | A config file, then five CLI commands for layout, key and permissions | Two environment variables |
| License | Apache 2.0 | AGPL 3.0 | Apache 2.0 |
| Project age | About ten years of releases | Several years of releases | 1.0.0 released in September 2026 |

Notes on the evidence:

- SeaweedFS and RustFS passed every step in three consecutive runs. Garage failed the same four steps in all three.
- The Garage failure is specific: the Iceberg S3 client's writes are rejected with `Invalid payload signature`, while writes from boto3 and from Spark's `s3a` client succeed. The three later failures follow from the first, because the table is never created. A client-side setting may work around it. That was not pursued, since two candidates work with default settings and a workaround is one more thing for a learner to get wrong.
- Memory is a single reading per run and varied a lot for RustFS, which read 33 MiB on two runs of the `latest` image and 108 MiB on the run of `1.0.0`. Treat the memory row as "all three are small", not as a ranking. Experiment B measures memory properly.
- The run that tested `latest` for RustFS and the run that tested `1.0.0` gave the same pass and fail results.

## Decision

**RustFS**, pinned to `1.0.0`, with SeaweedFS as the documented fallback. Confirmed by the author on 2026-11-11.

Garage is ruled out by the Iceberg failure.

Between the two that pass, the tests do not separate them, so the choice rests on what a beginner experiences:

- RustFS is configured with two environment variables and includes a web console, which the module 0 lab uses to let learners see their buckets and files.
- It behaves like MinIO, so the large body of existing tutorials and answers still helps a learner who searches for an error.
- It has the smaller image.

The argument for SeaweedFS is maturity. It has a decade of releases behind it, where RustFS reached 1.0 two months before this record.

## Consequences

- Every service talks to the storage through the S3 API only, with the endpoint and credentials taken from `.env`. Nothing in the course may depend on a RustFS-specific feature. This keeps the fallback real: switching to SeaweedFS is a change to one Compose service and one credentials file.
- The image is pinned to an exact version and updated through Dependabot, so a release that breaks the course is caught by the checkpoint in CI before learners meet it.
- The experiment stays in the repository and can be re-run against any new version of any candidate.

Revisit this decision if RustFS changes its license, stops publishing images, or fails the experiment on a new release.
