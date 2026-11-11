# Course constitution

These rules apply to every module, lesson, lab and line of code in this course. A spec, plan or pull request that conflicts with them is wrong until this file is changed first.

## 1. Purpose

Teach a learner to build a small but complete data platform, from raw files to an AI application on top of curated data, using tools that are current and widely used in industry.

The course serves two uses with the same material:

- **Self-paced.** Anyone can clone the repository and study alone, at no cost.
- **Instructor-led.** The author teaches cohorts from the same material, with a separate private instructor kit (slides, annotated solutions, grading rubrics).

The public repository is the complete course. The instructor kit only adds to it.

## 2. Principles

1. **English only.** Lessons, code, comments, commit messages and specs are written in English.
2. **One project, start to finish.** Every module adds a piece to the same platform. There are no throwaway examples.
3. **Runs on a laptop.** The default path needs Docker and nothing else: no cloud account, no credit card, no paid API. Cloud and paid services appear only as clearly marked optional tracks.
4. **Current stack.** Tools are chosen because they are current and maintained, not because an earlier version of the course used them. Every tool is pinned to an exact version in the file that uses it, and `docs/stack.md` lists every tool and where its version is pinned.
5. **Verifiable outcomes.** Every module ends in a checkpoint the learner can run. The same checks run in CI.
6. **Explain production.** When the laptop version differs from what a team would run in production, the lesson says so and describes the production alternative.
7. **No secrets in the repository.** Credentials live in a local `.env` that is git-ignored. The repository ships `.env.example` only.

## 3. Module format

Every module lives in `modules/NN-slug/` and contains the same parts:

| Part | File or folder | Content |
| --- | --- | --- |
| Lesson | `README.md` | Concepts, kept short. What, why, and how it is done in production |
| Lab | `lab/` | A guided, step-by-step build of this module's piece of the platform |
| Exercise | `exercise/` | A task the learner solves alone, extending the lab |
| Solution | `solution/` | A reference solution to the exercise |
| Checkpoint | `checkpoint/` | An automated check that the module's acceptance criteria hold |

Learners do the exercise by editing the files in `exercise/` in place. Checkpoints ignore changes there, so a learner's own work never makes a checkpoint fail.

## 4. Spec-driven workflow

Content is written from specs, one module at a time.

1. **Spec** (`specs/modules/NN-slug/spec.md`): learning objectives, what the learner builds, acceptance criteria, out of scope. No implementation detail.
2. **Review.** The author approves the spec before anything else is written.
3. **Plan** (`plan.md`): lesson outline, technical decisions, files to create.
4. **Tasks** (`tasks.md`): small, ordered, individually verifiable tasks.
5. **Implementation.** Lesson, lab, exercise, solution and checkpoint.
6. **Verification.** The checkpoint passes locally and in CI, on a clean machine.

Acceptance criteria are written so they can be checked by a command. They become the learner's checkpoint and the CI test.

A later module's spec is not written until the previous module is implemented. What is learned building module N changes module N+1.

## 5. Definition of done

A module is done when:

- its checkpoint passes in CI from a clean clone;
- the lesson, lab, exercise and solution exist and follow the module format;
- a learner who completed the previous modules can finish it without outside help;
- every tool it uses is listed in `docs/stack.md`, with the file where its version is pinned;
- every table it produces has at least one data quality check and an entry in the data dictionary;
- the root `README.md` syllabus links to it.

## 6. Data

The project uses the IMDb Non-Commercial Datasets. The data is never committed to this repository: a script downloads it to the learner's machine. Other sources may be added in later iterations.

## 7. Licensing

- **Lessons, text and diagrams:** Creative Commons Attribution-NonCommercial-ShareAlike 4.0 (CC BY-NC-SA 4.0). Anyone may study, share and adapt the material with credit, for non-commercial purposes, under the same license.
- **Code:** MIT.

The author keeps the right to use the material commercially.
