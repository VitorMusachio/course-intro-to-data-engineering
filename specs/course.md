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
4. Model data dimensionally and document it.
5. Orchestrate a pipeline end to end, with scheduling and backfills.
6. Test data, enforce schema contracts and run those checks in CI.
7. Serve curated data to a BI tool.
8. Build an AI application on top of curated data: an embeddings pipeline, retrieval-augmented generation with a measured evaluation, and an agent that queries the gold layer.
9. Explain, for each piece, how the laptop setup differs from a production deployment.

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
| 8 | Data quality and CI | Data tests, schema contracts and a CI pipeline that blocks regressions | dbt tests, GitHub Actions |
| 9 | Serving and BI | A dashboard on the gold layer | Trino, Metabase |
| 10 | AI on the data platform | An embeddings pipeline, RAG with evaluation, and an agent that queries the gold layer | Postgres with pgvector, a local model, MCP |
| 11 | Capstone | The whole project, documented and published. Optional cloud deployment track | Everything above, optional cloud |

Modules are specified and built in order. This table is the intent; each module's own spec is the authority once it exists.

## 5. Stack decisions

| Concern | Choice | Notes |
| --- | --- | --- |
| Orchestration | Airflow 3.x | The 2.x line reached end of life in April 2026 |
| Object storage, local | SeaweedFS, Garage or RustFS | To be chosen by a compatibility test with Iceberg and Spark. MinIO is excluded: its community edition is no longer maintained |
| Object storage, cloud track | Cloudflare R2 | Optional. S3-compatible, with a free tier |
| Processing | Spark 4.x | |
| Table format | Iceberg | |
| Query engine | Trino | |
| Transformation | dbt | |
| Streaming | Kafka | |
| BI | Metabase | |
| Vector search | Postgres with pgvector | |
| LLM | A local model in the labs | Each lesson describes the production alternative with a hosted API |

Exact versions are pinned when the environment is built and recorded in `docs/stack.md`.

## 6. Constraints

- The default path runs entirely on the learner's machine with Docker.
- Services are grouped so a learner starts only what the current module needs, not the whole platform at once.
- Target hardware: to be validated in module 0 (see open questions).

## 7. Out of scope

- Data science and model training.
- Kubernetes and infrastructure as code, beyond a mention in the cloud track.
- Vendor-specific warehouses (Snowflake, BigQuery, Redshift, Databricks). Lessons mention how the concepts map to them.
- Real-time stream processing frameworks beyond producing and consuming with Kafka.

## 8. Open questions

1. **IMDb data and paid cohorts.** IMDb licenses these datasets for personal and non-commercial use only and does not allow republishing them. Self-paced, free study fits that. Teaching paid cohorts with the same data may not. Decide before the first paid cohort whether to seek permission, or to switch the project to an openly licensed source.
2. **Minimum hardware.** Is 8 GB of RAM enough if only one module's services run at a time, or does the course require 16 GB?
3. **Local object storage.** Which of the three candidates passes the compatibility test.
4. **Local model.** Which model and runtime are small enough for a laptop and good enough for the RAG and agent labs.
