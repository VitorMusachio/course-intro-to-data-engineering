# Experiment B: memory

Question: how much memory does a learner's machine need for this course?

## What it measures

Three scenarios, each sampled with `docker stats` every three seconds while it works. The report gives the peak for each container and the peak of the total across all containers at the same moment.

| Scenario | What runs |
| --- | --- |
| `base` | The module 0 environment: RustFS and the toolbox |
| `lakehouse` | An estimate of the heaviest single module: RustFS, an Iceberg REST catalog, Trino, and a Spark job that writes and aggregates ten million rows |
| `datahub` | DataHub alone, from its official quickstart, with its sample metadata loaded |

## What it does not measure

- Docker Desktop's own overhead on macOS and Windows, where containers run inside a virtual machine. The figures here are from Linux.
- The operating system, the browser and the editor a learner keeps open.
- Larger data. Peak memory of the engines is set mostly by their configured limits, not by the size of the tables.

## How to run it

In GitHub Actions: the "Experiments" workflow, job "Memory". Locally:

```
bash experiments/memory/run.sh lakehouse
```

## Result

Recorded in `docs/decisions/0002-hardware-requirement.md`.
