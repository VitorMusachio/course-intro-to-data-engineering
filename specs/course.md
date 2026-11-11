# Course spec: Introduction to Data Engineering

Status: draft, awaiting author review.

## 1. Who this is for

A learner who can already program a little and wants to become productive in a data engineering role.

**Assumed before starting**

- Basic Python: variables, functions, loops, reading a traceback.
- Basic SQL: `SELECT`, `WHERE`, `JOIN`, `GROUP BY`.
- Comfortable in a terminal and with Git basics (clone, commit, push).
- A computer that can run Docker (see section 6).

**Not assumed**

- Any experience with Spark, Airflow, dbt, Kafka, Docker Compose or cloud services.
- Any background in machine learning or AI.

## 2. What the learner can do at the end

1. Ingest data in batch, incremental and streaming modes, and explain when each fits.
2. Store data in object storage using open file and table formats.
3. Transform data with Spark and with SQL (dbt), following a medallion layout: bronze, silver, gold.
4. Model data dimensionally.
5. Orchestrate a pipeline end to end, with scheduling and backfills.
6. Write data quality checks at every layer, enforce schema contracts, monitor freshness and run those checks in CI.
7. Serve curated data to a BI tool.
8. Build an AI application on top of curated data: an embeddings pipeline, retrieval-augmented generation with a measured evaluation, and an agent that queries the gold layer.
9. Document a data platform and make it discoverable: a data dictionary, lineage, the decisions behind it, and a data catalog.
10. Explain, for each piece, how the laptop setup differs from a production deployment.

## 3. The project

One platform, built module by module, on IMDb data.

```
IMDb datasets
     |
     v
[ingestion] --> bronze (raw files, object storage)
                   |
                   v  Spark
                silver (cleaned, typed, Iceberg tables)
                   |
                   v  dbt on Trino
                 gold (facts and dimensions)
                   |
        +----------+-----------+
        v                      v
   BI dashboard         AI application
    (Metabase)     (embeddings, RAG, agent)

Airflow orchestrates every step. CI runs the data tests.
```

## 4. Syllabus

| # | Module | The learner builds | Stack |
| --- | --- | --- | --- |
| 0 | Setup and course tour | A running local environment and a map of the final architecture | Docker Compose, uv, Git |
| 1 | Python for data engineering | Typed, tested scripts that read and write CSV, JSON and Parquet | Python, Polars, DuckDB, pytest |
| 2 | Object storage and file formats | The bronze layer: raw, partitioned data in a bucket | S3-compatible storage, Parquet |
| 3 | Ingestion patterns | Three ingestions of the same source: batch, incremental, streaming | Python, Kafka |
| 4 | Processing with Spark | The silver layer: cleaning and standardizing with the DataFrame API and Spark SQL | Spark |
| 5 | The lakehouse | Tables with ACID guarantees, schema evolution and time travel, queried with SQL | Iceberg, Trino |
| 6 | Modeling and transformation with dbt | The gold layer: facts and dimensions, tested and documented | dbt, Trino |
| 7 | Orchestration with Airflow | DAGs that connect ingestion, Spark and dbt, with backfills and asset-based scheduling | Airflow 3 |
| 8 | Data quality and CI | A quality strategy across all layers: data tests, schema contracts, freshness checks, failures surfaced in the orchestrator, and a CI pipeline that blocks regressions | dbt tests, GitHub Actions |
| 9 | Serving, BI and the data catalog | A dashboard on the gold layer, and a catalog where every table, its owner, its lineage and its test results can be found | Trino, Metabase, DataHub |
| 10 | AI on the data platform | An embeddings pipeline, RAG with evaluation, and an agent that queries the gold layer | Postgres with pgvector, a local model, MCP |
| 11 | Capstone | The whole project, documented and published. Optional cloud deployment track | Everything above, optional cloud |

Modules are specified and built in order. This table is the intent; each module's own spec is the authority once it exists.

### Threads that run through every module

Two topics are not left to a single module. Each module that produces data contributes to both.

**Data quality**

| Where | What the learner adds |
| --- | --- |
| Module 1 | Unit tests for transformation code |
| Modules 2 and 3 (bronze) | Checks on arrival: expected files, schema, row counts |
| Modules 4 and 5 (silver) | Checks on content: nulls, uniqueness, types, accepted values |
| Module 6 (gold) | dbt tests on keys, relationships and business rules |
| Module 7 | Checks run as pipeline steps, and a failed check stops the run |
| Module 8 | The pieces become one strategy: which check belongs at which layer, schema contracts, freshness, and CI |

**Documentation**

| Where | What the learner adds |
| --- | --- |
| Every module that produces data | Entries in the project's data dictionary: each table, each column, its meaning and its source |
| Module 6 | Generated dbt documentation with lineage |
| Module 9 | A data catalog in DataHub, fed with metadata from the tables, dbt and the orchestrator |
| Modules with a design choice | A short decision record: the options, the choice, the reason |
| Module 11 | The project README a hiring manager would read: architecture, how to run it, what it demonstrates |

## 5. Stack decisions

| Concern | Choice | Notes |
| --- | --- | --- |
| Orchestration | Airflow 3.x | The 2.x line reached end of life in April 2026 |
| Object storage, local | RustFS | Chosen by experiment: see `docs/decisions/0001-object-storage.md`. SeaweedFS is the fallback. MinIO is excluded: its community edition is no longer maintained |
| Object storage, cloud track | Cloudflare R2 | Optional. S3-compatible, with a free tier |
| Processing | Spark 4.x | |
| Table format | Iceberg | |
| Query engine | Trino | |
| Transformation | dbt | |
| Streaming | Kafka | |
| BI | Metabase | |
| Data quality | dbt tests | The single quality tool from the gold layer on. Earlier layers use plain Python checks. No dedicated quality framework is added |
| Data catalog | DataHub | Runs only in module 9. It needs about 4 GiB by itself, so its lab is optional on 8 GB machines |
| Vector search | Postgres with pgvector | |
| LLM | A local model in the labs | Each lesson describes the production alternative with a hosted API |

Exact versions are pinned when the environment is built and recorded in `docs/stack.md`.

## 6. Constraints

- The default path runs entirely on the learner's machine with Docker.
- Services are grouped so a learner starts only what the current module needs, not the whole platform at once.
- Hardware: 8 GB of memory minimum, 16 GB recommended. On 8 GB machines the hands-on DataHub lab in module 9 is replaced by a recorded walkthrough. See `docs/decisions/0002-hardware-requirement.md`.

## 7. Out of scope

- Data science and model training.
- Kubernetes and infrastructure as code, beyond a mention in the cloud track.
- Vendor-specific warehouses (Snowflake, BigQuery, Redshift, Databricks). Lessons mention how the concepts map to them.
- Real-time stream processing frameworks beyond producing and consuming with Kafka.

## 8. Deferred decisions

Each of these has an owner moment. None blocks module 0.

| Question | Decision | Resolved when |
| --- | --- | --- |
| IMDb data and paid cohorts | Keep IMDb for now. IMDb licenses these datasets for personal and non-commercial use only and does not allow republishing them, which fits free self-paced study but may not fit paid cohorts. Either seek permission or switch to an openly licensed source | Before the first paid cohort |
| Local model and runtime | Chosen from what is available when the module is specified | Module 10 spec |

## 9. Supported platforms

Linux, macOS, and Windows through WSL2. Native Windows is not supported.
