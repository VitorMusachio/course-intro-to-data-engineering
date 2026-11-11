# Module 0 spec: Setup and course tour

Status: draft, awaiting author review.

## 1. Why this module exists

Every later module assumes a working environment and a shared picture of what is being built. Learners who fight their setup in module 3 often quit. This module removes that risk first and shows the destination before the journey starts.

## 2. Learning objectives

After this module the learner can:

1. Describe the platform they will build and name the role of each component.
2. Explain the medallion layout (bronze, silver, gold) in one sentence per layer.
3. Start, inspect and stop the course environment with Docker Compose.
4. Start only the services a given module needs.
5. Download the IMDb datasets to their machine with the provided script.
6. Run a module checkpoint and read its result.

## 3. What the learner builds

- A clone of the repository with a local `.env` created from `.env.example`.
- A running base environment: object storage, plus whatever module 1 needs.
- A local copy of the IMDb datasets, outside version control.
- A passing module 0 checkpoint.

## 4. What the repository must provide

- A root `README.md` with the course description, prerequisites, syllabus and a quick start.
- A Docker Compose setup where services are grouped by module.
- `.env.example` with every variable documented, and `.env` git-ignored.
- A data download script that is safe to run twice.
- A single command to run any module's checkpoint.
- `docs/stack.md` listing every tool and its pinned version.
- An architecture diagram of the final platform.
- A CI workflow that runs the module 0 checkpoint on every pull request.
- `LICENSE` (MIT, code) and `LICENSE-CONTENT.md` (CC BY-NC-SA 4.0, lessons).

## 5. Acceptance criteria

Each criterion is checked by a command. Together they are the module 0 checkpoint.

1. From a clean clone, with only Docker installed, one documented command starts the base environment and exits successfully.
2. Every service in the base environment reports healthy within 3 minutes.
3. The object storage answers an S3 API call: a bucket can be created, an object written, read back and deleted.
4. The data download script fetches the IMDb files into the git-ignored data folder, and a second run downloads nothing.
5. `git status` shows no untracked or modified files after the environment has started and the data has been downloaded.
6. No file in the repository contains a credential. `.env` is absent from version control.
7. One documented command stops the environment and removes its containers.
8. The checkpoint command prints one pass or fail line per criterion above and exits non-zero on any failure.
9. The same checkpoint passes in CI.

## 6. Out of scope

- Teaching Docker itself. The lesson links to a primer and explains only the commands the course uses.
- Installing or configuring Spark, Airflow, Trino, dbt or Kafka. Each arrives in its own module.
- Any cloud setup.

## 7. Open questions

1. **Minimum hardware.** Measure the base environment's memory use and set the stated requirement from the measurement.
2. **Local object storage.** Run the compatibility test and record the choice, with the reason, in `docs/stack.md`.
3. **Checkpoint tooling.** A plain shell script, pytest, or a small task runner. To be decided in the plan, favouring whatever a beginner can read.
4. **Operating systems.** Which are supported and tested: Linux and macOS for certain. Windows through WSL2 is likely but needs a decision.
