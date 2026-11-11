# Introduction to Data Engineering

A hands-on course in which you build one small but complete data platform on your own laptop, from raw files to an AI application that answers questions from curated data.

> **Status: under construction.** Module 0 is ready. The other modules are being written one at a time. See the [syllabus](#syllabus) for what exists today.

## What you build

One project, from the first module to the last, on real data from IMDb.

You ingest the data, store it in a data lake, clean it with Spark, organize it as Iceberg tables, model it with dbt, schedule everything with Airflow, test it, document it, put a dashboard on it, and finally build an AI application that reads it.

The whole platform is drawn in [`docs/architecture.md`](docs/architecture.md).

## Who it is for

Someone who can program a little and wants to work as a data engineer.

You should already be comfortable with:

- basic Python: variables, functions, loops;
- basic SQL: `SELECT`, `WHERE`, `JOIN`, `GROUP BY`;
- a terminal, and cloning a repository with Git.

You do not need any experience with Docker, Spark, Airflow, dbt, cloud services or AI.

## What you need

| | Minimum | Recommended |
| --- | --- | --- |
| Memory | 8 GB | 16 GB |
| Free disk space | 10 GB | 20 GB |
| Operating system | Linux, macOS, or Windows with WSL2 | |
| Software | [Docker](https://docs.docker.com/get-started/get-docker/) | |

Everything runs on your machine. There is no cloud account to create and nothing to pay for.

With 8 GB of memory you can do every module except the hands-on data catalog lab in module 9, which has a recorded walkthrough for that case. The reasoning is in [`docs/decisions/0002-hardware-requirement.md`](docs/decisions/0002-hardware-requirement.md).

## Quick start

```
git clone https://github.com/VitorMusachio/course-intro-to-data-engineering.git
cd course-intro-to-data-engineering
cp .env.example .env
./course doctor
./course up
./course data
./course check 0
```

`./course data` downloads about 1.9 GB.

Those commands are explained one by one in [module 0](modules/00-setup/README.md). Start there.

## Syllabus

| # | Module | You build | Status |
| --- | --- | --- | --- |
| 0 | [Setup and course tour](modules/00-setup/README.md) | A running local environment and a map of the platform | Ready |
| 1 | Python for data engineering | Typed, tested scripts that read and write CSV, JSON and Parquet | Planned |
| 2 | Object storage and file formats | The bronze layer: raw, partitioned data in a bucket | Planned |
| 3 | Ingestion patterns | Batch, incremental and streaming ingestion of the same source | Planned |
| 4 | Processing with Spark | The silver layer: cleaned and standardized data | Planned |
| 5 | The lakehouse | Iceberg tables with safe updates, schema changes and time travel | Planned |
| 6 | Modeling and transformation with dbt | The gold layer: facts and dimensions, tested and documented | Planned |
| 7 | Orchestration with Airflow | Pipelines that run every step in order, on a schedule | Planned |
| 8 | Data quality and CI | Data tests, schema contracts and a pipeline that blocks bad changes | Planned |
| 9 | Serving, BI and the data catalog | A dashboard and a catalog on the gold layer | Planned |
| 10 | AI on the data platform | Embeddings, retrieval-augmented generation and an agent over your tables | Planned |
| 11 | Capstone | The whole project, documented and published | Planned |

## How each module works

Every module has the same five parts:

| Part | Where | What it is |
| --- | --- | --- |
| Lesson | `README.md` | The concepts, kept short, and how the same thing is done in a company |
| Lab | `lab/` | A guided, step-by-step build |
| Exercise | `exercise/` | A task you solve yourself |
| Solution | `solution/` | A reference answer, with notes on what to notice |
| Checkpoint | `checkpoint/` | An automated check that you reached the module's goals |

You run a module's checkpoint with `./course check <number>`.

## How this course is written

The course is built from specifications. Each module starts as a spec that is reviewed before any content exists, and the spec's acceptance criteria become the module's checkpoint.

- [`specs/constitution.md`](specs/constitution.md): the rules every module follows
- [`specs/course.md`](specs/course.md): audience, learning outcomes and stack
- [`specs/modules/`](specs/modules/): the spec, plan and tasks of each module
- [`docs/decisions/`](docs/decisions/): why each tool was chosen, with the evidence
- [`docs/stack.md`](docs/stack.md): every tool the course uses

## Data

The labs use the [IMDb Non-Commercial Datasets](https://developer.imdb.com/non-commercial-datasets/). They are downloaded to your machine by `./course data` and are not part of this repository. IMDb provides them for personal and non-commercial use, under its own terms.

## License

- Lessons, text and diagrams: [CC BY-NC-SA 4.0](LICENSE-CONTENT.md). You may share and adapt them with credit, for non-commercial purposes.
- Code: [MIT](LICENSE).
