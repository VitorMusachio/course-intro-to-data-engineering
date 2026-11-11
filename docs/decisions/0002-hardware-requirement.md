# 0002. Hardware requirement

Status: proposed, awaiting the author's decision
Date: 2026-11-11

## Context

The course promises to run on a learner's laptop. That promise needs a number: how much memory the machine must have. The spec for module 0 says the number comes from a measurement, not from a guess.

## Evidence

Three scenarios were run in GitHub Actions on Linux (`experiments/memory/`, workflow "Experiments"). Memory was sampled with `docker stats` about every five seconds. "Peak total" is the largest sum across all containers at one moment.

| Scenario | What ran | Peak total |
| --- | --- | --- |
| Base | RustFS and the toolbox | 93 MiB |
| Lakehouse | RustFS, an Iceberg REST catalog, Trino, and a Spark job writing and aggregating 10 million rows | 2,564 MiB |
| DataHub | DataHub 1.7 quickstart, alone, with its sample metadata | 4,107 MiB |

Peak per container:

| Lakehouse | MiB | | DataHub | MiB |
| --- | --- | --- | --- | --- |
| Trino | 1,991 | | Metadata service (GMS) | 1,485 |
| Spark | 1,224 | | OpenSearch | 1,183 |
| RustFS | 409 | | System update (runs once, then exits) | 872 |
| REST catalog | 194 | | Kafka broker | 488 |
| | | | Frontend | 429 |
| | | | MySQL | 382 |
| | | | Actions | 144 |

What these numbers do and do not say:

- **Trino takes what it is given.** Its image sets the Java heap to 80% of the memory it can see. It used 2 GiB here because the workload was small, not because 2 GiB is its limit. On a learner's machine it must be capped explicitly.
- **Spark's 1.2 GiB is its configured limit**, the default 1 GiB driver plus overhead. It does not grow with the data; larger data makes it slower or makes it fail.
- **DataHub needs about 4 GiB by itself.** In module 9 it runs next to Trino and RustFS, which it reads metadata from, so that module needs roughly 5.5 to 6 GiB for containers.
- **Not measured yet:** Airflow (module 7), Kafka as used in module 3, Metabase, and the local language model (module 10). Airflow in particular runs several processes and a database.
- **Not included:** the operating system, a browser and an editor, and the overhead of Docker Desktop's virtual machine on macOS and Windows. As a rule of thumb, containers can use about half of a laptop's memory.
- Sampling every five seconds can miss a short spike. Read each figure as "at least".

Applying the rule of thumb:

| Machine | Memory available to containers | Lakehouse modules (about 2.6 GiB) | Catalog module (about 6 GiB) |
| --- | --- | --- | --- |
| 8 GB | about 4 GiB | fits | does not fit |
| 16 GB | about 8 GiB | fits | fits |

## Options

**A. Require 16 GB for the whole course.** One simple number, and every module works for everyone who meets it. It excludes learners with 8 GB machines from the start, for the sake of one module.

**B. 8 GB minimum, 16 GB recommended, with the DataHub lab optional on 8 GB.** Everything except the hands-on part of module 9 runs on 8 GB. On an 8 GB machine, the learner reads the catalog lesson and follows a recorded walkthrough instead of running DataHub, and the catalog part of that module's checkpoint is skipped. The course states this limit up front.

**C. Replace DataHub with a lighter catalog.** Keeps one requirement for everyone, but gives up the tool the author chose, and a lighter tool would need its own evaluation.

## Decision

Proposed: **option B**.

It keeps the course open to the most learners, keeps DataHub, and is honest about the one place where 8 GB is not enough. The author decides.

## Consequences

Whichever option is chosen:

- `compose.yaml` sets explicit memory limits: a fixed heap for Trino and a stated driver memory for Spark. No service is left to size itself from the host.
- `./course doctor` reads how much memory Docker has and warns before a module starts if it is not enough for that module.
- Each later module measures its own services when it is built and adds a row to this record. If Airflow or the local model turns out heavier than the lakehouse scenario, this decision is revisited before that module is declared done.
- The README states the requirement from this record, with the caveat about module 9 if option B stands.
