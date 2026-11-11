# Module 0 tasks

Status: confirmed by the author. Implements `plan.md` in this folder.

Tasks run in order. Each one is a single pull request unless noted, and each is done only when its "Done when" line is true. Tasks marked **Author** need the course author; the rest can be written by an assistant and reviewed.

## Phase A: skeleton

- [x] **T01. Repository skeleton.** `.gitignore` (covering `.env` and `data/`), `.env.example`, `LICENSE`, `LICENSE-CONTENT.md`, the folder layout from the plan, and stubs for `docs/stack.md` and `docs/data-dictionary.md`.
  Done when: the tree matches section 2 of the plan and `.env` cannot be committed.

- [x] **T02. Toolbox image.** `docker/toolbox/Dockerfile` with a pinned Python, uv, pytest and an S3 client.
  Done when: the image builds in CI and `pytest --version` runs inside it.

## Phase B: experiments

- [x] **T03. Experiment A, object storage.** `experiments/object-storage/` and a manual workflow that runs the six steps from the plan against SeaweedFS, Garage and RustFS.
  Done when: the workflow has run and its log shows a pass or fail per step per candidate.

- [x] **T04. Decision record 0001.** `docs/decisions/0001-object-storage.md`: the options, the results table, the choice, the reason. **Author** confirms the choice.
  Done when: the record is merged and names one candidate.

- [x] **T05. Experiment B, memory.** A manual workflow that measures peak memory for the base environment, for Spark plus Trino plus storage, and for DataHub alone.
  Done when: the workflow has run and its log shows the three figures.

- [x] **T06. Decision record 0002.** `docs/decisions/0002-hardware-requirement.md`, setting the minimum and recommended memory. If DataHub alone exceeds the minimum, the record lays out the options. **Author** decides.
  Done when: the record is merged and states one requirement.

## Phase C: environment

- [x] **T07. Base environment.** `compose.yaml` with the `base` profile: the chosen object storage and the toolbox, with healthchecks and pinned tags.
  Done when: `docker compose --profile base up --wait` succeeds in CI.

- [x] **T08. The `course` command.** `up`, `down`, `status`, `check`, `doctor`, with the module-to-profile mapping.
  Done when: each command works in CI under current bash, the script parses under bash 3.2 and passes shellcheck, and `./course up` fails with a readable message when `.env` is missing. A full run under bash 3.2 is part of T17, on macOS.

- [x] **T09. Data download.** `scripts/download_data.py` and `./course data`, with the manifest described in the plan.
  Done when: the first run downloads seven files, and a second run reports zero downloads.

## Phase D: checkpoint and CI

- [ ] **T10. Module 0 checkpoint.** `modules/00-setup/checkpoint/`: one pytest test per criterion that can be checked from inside the platform, plus the host checks in `./course check`.
  Done when: `./course check 00` prints nine lines, one per criterion, and exits non-zero if any fails.

- [ ] **T11. CI workflow.** `.github/workflows/checkpoints.yml` as described in the plan, including the data cache, the "no containers left" and "git status clean" assertions, and a secret scan.
  Done when: the workflow is green on a pull request, and red on a branch where one criterion is deliberately broken.

## Phase E: content

- [ ] **T12. Architecture diagram.** `docs/architecture.md`, as a diagram that renders on GitHub.
  Done when: every component named in the course spec appears, with its module number.

- [ ] **T13. Lesson.** `modules/00-setup/README.md`, following the outline in the plan.
  Done when: all eight sections exist and every command in the lesson has been run as written.

- [ ] **T14. Lab, exercise and solution.**
  Done when: following the lab from a clean clone ends in a passing checkpoint, and the solution's commands complete the exercise.

- [ ] **T15. Root README and `docs/stack.md`.** Course description, prerequisites, hardware requirement from record 0002, syllabus with a link to module 0, quick start. Every tool and pinned version in `docs/stack.md`.
  Done when: a newcomer can go from the README to a passing module 0 checkpoint using only what is written there.

## Phase F: verification

- [ ] **T16. Clean-machine check, Linux.** Covered by CI.
  Done when: T11 is green on `main`.

- [ ] **T17. Clean-machine check, macOS.** **Author**, from a fresh clone with no leftover containers, volumes or images from earlier work.
  Done when: the lab is completed as written and the checkpoint passes. Anything that needed outside knowledge is filed as an issue and fixed in the lesson.

- [ ] **T18. Clean-machine check, WSL2.** **Author**.
  Done when: same as T17, on Windows through WSL2.

- [ ] **T19. Definition of done.** Walk the five points in section 5 of the constitution against module 0.
  Done when: all five hold, and the module 1 spec can begin.

## Checklist for T17 and T18

1. Install Docker following only the lesson.
2. Clone the repository.
3. Create `.env` from `.env.example`.
4. `./course doctor`
5. `./course up`
6. `./course data`
7. `./course check 00`
8. Do the exercise without looking at the solution.
9. `./course down`
10. Note the total time, and every point where the lesson was not enough.
