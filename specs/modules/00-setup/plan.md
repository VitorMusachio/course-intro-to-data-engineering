# Module 0 plan: Setup and course tour

Status: decisions in section 3 confirmed by the author. Implements `spec.md` in this folder.

## 1. Approach in one paragraph

The learner interacts with the course through one small command, `./course`, which wraps Docker Compose. Everything else, including Python and the checkpoint tests, runs inside containers, so the only thing a learner installs is Docker. Two unknowns from the spec (which object storage, how much memory) are settled by experiments that run in GitHub Actions before the environment is built, and each ends in a written decision record.

## 2. Repository layout after this module

```
course                      the learner's command (bash)
compose.yaml                all services, grouped by Compose profile
.env.example                every variable, documented
README.md                   course description, prerequisites, syllabus, quick start
LICENSE                     MIT, code
LICENSE-CONTENT.md          CC BY-NC-SA 4.0, lessons
docker/
  toolbox/Dockerfile        Python, uv, pytest and the S3 client used by checkpoints
config/
  sources.yml               declares which files enter the pipeline
scripts/
  download_data.py          downloads what sources.yml declares, idempotent
data/                       git-ignored; datasets land here
docs/
  architecture.md           diagram of the final platform
  stack.md                  every tool and where its version is pinned
  data-dictionary.md        starts here, grows with every module
  decisions/                one short record per design decision
experiments/                throwaway code behind the decision records
modules/
  00-setup/
    README.md               lesson
    lab/
    exercise/
    solution/
    checkpoint/             pytest tests, one per acceptance criterion
.github/workflows/
  checkpoints.yml           runs module checkpoints on every pull request
  experiments.yml           manual trigger, runs the experiments below
```

## 3. Decisions

### 3.1 The learner's command

A single bash script at the repository root. Bash is present on Linux, macOS and WSL2, which are the supported platforms, so nothing extra is installed.

| Command | What it does |
| --- | --- |
| `./course up [module]` | Starts the services that module needs. With no argument, starts the base environment |
| `./course down` | Stops the environment and removes its containers |
| `./course status` | Shows each service and its health |
| `./course data` | Downloads the IMDb datasets |
| `./course check <module>` | Runs that module's checkpoint |
| `./course run <command>` | Runs a command in the toolbox |
| `./course shell` | Opens a shell in the toolbox |
| `./course doctor` | Checks Docker itself: installed, running, enough memory allocated |

Make was considered and rejected: it is not installed by default on every supported platform, and its syntax is one more thing for a beginner to read.

### 3.2 Checkpoint tooling

**Decision: pytest, run inside the toolbox container.**

| Option | For | Against |
| --- | --- | --- |
| Shell script | Nothing to install, readable for trivial checks | Checks on data (row counts, duplicates, schemas) become unreadable. Every module would reinvent its output format |
| **pytest in a container** | One test per acceptance criterion, so the pass or fail line per criterion comes for free. Learners meet pytest in module 1 and then can read every checkpoint. Data checks are natural in Python. Same command locally and in CI | Needs a Python image, which the course needs anyway |
| Task runner (just, Task) | Nice command names | Another tool to install and learn, and it still needs something to write the checks in |

Each test is named after its criterion and carries the criterion's text as its docstring, so a failure tells the learner which criterion failed in the spec's own words.

Some criteria are about the host, not the platform: the environment starts from a clean clone, `git status` is clean afterwards, and `down` removes the containers. A test running inside a container cannot see those. They are checked by `./course check` on the host before it hands over to pytest, and again by the CI workflow steps.

### 3.3 Compose design

- One `compose.yaml`. Each service declares the profiles it belongs to.
- Profile `base`: object storage and the toolbox. This is all module 0 starts.
- Later modules add profiles (`spark`, `kafka`, `trino`, `airflow`, `catalog`, and so on). The mapping from module number to profiles lives in the `course` script, so the learner types a module number and never a profile name.
- Every service has a healthcheck. `./course up` waits for health and fails with a clear message after 3 minutes.
- Image tags are pinned to exact versions, never `latest`.
- Named volumes hold service state. `./course down` keeps them; `./course down --wipe` removes them.

### 3.4 Data download

- Sources and files are declared in `config/sources.yml`, not in code. The script downloads what is declared there, and later modules read the same file. It starts with the seven IMDb dataset files.
- The script validates the declarations before downloading anything: required fields, an https URL, a target folder under `data/`, plain file names, and dataset names that are unique.
- The script records each file's size and last-modified header in a small manifest under `data/`. A second run compares against the server and skips files that have not changed. This is what satisfies "a second run downloads nothing".
- Files stay compressed on disk. Decompression is part of module 2, where file formats are taught.
- IMDb refreshes the data daily, so two learners can hold different snapshots. Checkpoints therefore assert on structure and invariants (columns, uniqueness, plausible ranges), never on exact row counts.

### 3.5 Experiments

Docker images cannot be pulled in the environment where these specs are written, so both experiments run as a manually triggered GitHub Actions workflow in this repository. Results are read from the workflow logs and written up as decision records.

**Experiment A: object storage.** For each of SeaweedFS, Garage and RustFS:

1. Start it with Compose and wait for health.
2. S3 round trip: create a bucket, write, read and delete an object.
3. Spark writes and reads Parquet through the S3 API.
4. Spark creates an Iceberg table, appends to it and reads an earlier snapshot.
5. Trino reads the same Iceberg table.
6. Record: which steps pass, image size, idle memory, start-up time.

The result also weighs how actively each project is maintained and its license. Outcome: `docs/decisions/0001-object-storage.md`.

Step 4 needs an Iceberg catalog. The experiment uses a minimal one to get a result; which catalog the course teaches is decided in the module 5 spec, not here.

**Experiment B: memory.** Measure peak memory of (a) the base environment, (b) the heaviest combination a single module will need, estimated as Spark plus Trino plus object storage, and (c) DataHub running alone. Outcome: `docs/decisions/0002-hardware-requirement.md`, which sets the requirement stated in the README.

### 3.6 CI

`checkpoints.yml` runs on every pull request: start the base environment, download the data, run the module 0 checkpoint, stop the environment, then assert that no containers remain and that `git status` is clean.

CI covers Linux only, because GitHub's macOS runners do not provide Docker. The author verifies macOS and WSL2 by hand before each module is declared done, following a short checklist in `tasks.md`.

The IMDb download is cached in CI so pull requests do not download it every time.

## 4. Lesson outline

`modules/00-setup/README.md`, in this order:

1. What you will build: the architecture diagram, one paragraph per component.
2. Bronze, silver, gold: one sentence each, and why layers exist.
3. Before you start: prerequisites, hardware, installing Docker. A separate section for WSL2.
4. The `./course` command.
5. Lab: clone, create `.env`, start the base environment, look at the object storage console, download the data, run the checkpoint.
6. Exercise: using only the toolbox, create a bucket, upload one of the IMDb files and list it. The solution shows the commands.
7. In production: how each piece of this laptop setup maps to a real deployment.
8. Troubleshooting: the five failures a beginner is most likely to hit.

## 5. How each acceptance criterion is verified

| # | Criterion | Verified by |
| --- | --- | --- |
| 1 | Clean clone starts with one command | CI step (Linux); manual checklist (macOS, WSL2) |
| 2 | Services healthy within 3 minutes | `./course up` timeout; pytest reads service health |
| 3 | S3 round trip works | pytest |
| 4 | Data downloads; second run downloads nothing | pytest, by running the script twice and reading its report |
| 5 | `git status` clean afterwards | `./course check` host step; CI step |
| 6 | No credentials in the repository | pytest scans tracked files; CI secret scan |
| 7 | One command stops and removes containers | CI step after `./course down` |
| 8 | One pass or fail line per criterion, non-zero exit on failure | pytest output format; CI asserts the exit code on a deliberately broken run |
| 9 | Checkpoint passes in CI | `checkpoints.yml` |

## 6. Risks

| Risk | Mitigation |
| --- | --- |
| None of the three storage candidates passes every step | The experiment reports partial results. The fallback is the candidate that passes Spark and Iceberg, with the Trino gap documented and revisited in module 5 |
| IMDb download is large or slow for learners | Measure in experiment B. If needed, add a `--sample` mode that downloads everything but builds a smaller working subset |
| A learner's Docker has too little memory allocated | `./course doctor` reads the allocation and warns before anything starts |
| The bash script behaves differently on macOS's older bash | Write to the common subset and run it under bash 3.2 in CI |
