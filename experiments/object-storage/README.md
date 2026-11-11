# Experiment A: object storage

Question: which S3-compatible object storage should the course run locally, now that MinIO's community edition is no longer maintained?

Candidates: SeaweedFS, Garage, RustFS.

## What it tests

For each candidate, in order:

1. The service starts and answers an authenticated S3 call.
2. S3 round trip: create a bucket, then write, read, list and delete an object.
3. Spark writes and reads Parquet through `s3a`.
4. Spark creates an Iceberg table, appends to it and reads an earlier snapshot.
5. Trino reads that Iceberg table, and writes a new one.
6. Measurements: image size, idle memory, start-up time.

A minimal Iceberg REST catalog sits between the engines and the storage. It is here only to make the test possible. Which catalog the course teaches is decided in the module 5 spec.

## How to run it

In GitHub Actions: the "Experiments" workflow, started by hand or by a pull request that touches this folder. Each candidate is one job, and each job's summary shows a results table.

Locally, with Docker:

```
bash experiments/object-storage/run.sh seaweedfs
```

The script always exits 0. A failing step is a finding, not an error.

## Result

Recorded in `docs/decisions/0001-object-storage.md`.
