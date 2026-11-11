# Module 0: Setup and course tour

By the end of this module you have the course environment running on your machine, the datasets downloaded, and a picture of what you will build in the modules that follow.

| | |
| --- | --- |
| Time | About 1 hour, most of it waiting for downloads |
| You need | A computer with 8 GB of memory or more, about 10 GB of free disk space, and an internet connection |
| You build | A running object storage, a toolbox for running code, and a local copy of the IMDb datasets |

**In this module**

1. [What you will build](#1-what-you-will-build)
2. [Bronze, silver, gold](#2-bronze-silver-gold)
3. [Before you start](#3-before-you-start)
4. [The course command](#4-the-course-command)
5. [Lab](#5-lab)
6. [Exercise](#6-exercise)
7. [In production](#7-in-production)
8. [Troubleshooting](#8-troubleshooting)

## 1. What you will build

A data platform is the set of tools that takes data from where it is produced to where it is useful. In this course you build a small one, piece by piece, on your own machine.

The data comes from IMDb: titles, people, ratings and credits for millions of films and series. By the last module, you can ask a question such as "which directors have the best-rated films of the 1990s?" and get the answer three ways: from a SQL query, from a dashboard, and from an AI application that reads your tables.

The full picture is in [`docs/architecture.md`](../../docs/architecture.md). Open it now and keep it nearby. Every module adds one box to that diagram.

In this module you add the first two:

- **Object storage.** A service that stores files and hands them back over the network. Everything in the platform reads from it and writes to it. Yours is called RustFS. It speaks the same protocol as Amazon S3, the most widely used object storage in the world, so what you learn here applies there.
- **The toolbox.** A container with Python and the libraries the course uses. It runs the course's scripts and checks, so you never have to install Python packages on your own machine.

## 2. Bronze, silver, gold

The platform keeps its data in three layers. You will hear these names in every module.

- **Bronze** keeps the data exactly as it arrived.
- **Silver** holds the same data after cleaning.
- **Gold** holds tables shaped for a purpose, such as a dashboard.

Why not clean the data once and keep only the result? Because cleaning involves decisions, and decisions are sometimes wrong. With the original data kept in bronze, a mistake in cleaning is fixed by running the cleaning again. Without it, the original is gone.

The files you download in this module are the raw material for the bronze layer.

## 3. Before you start

### What you should already know

- Enough Python to read a short script: variables, functions, loops.
- Enough SQL to read a query with `SELECT`, `WHERE`, `JOIN` and `GROUP BY`.
- How to use a terminal: change folders, run a command.
- The basics of Git: clone a repository.

### Your machine

| | Minimum | Recommended |
| --- | --- | --- |
| Memory | 8 GB | 16 GB |
| Free disk space | 10 GB | 20 GB |
| Operating system | Linux, macOS, or Windows with WSL2 | |

With 8 GB of memory you can do every module except the hands-on part of the data catalog in module 9, which has a recorded walkthrough for that case.

### Install Docker

Docker runs each tool of the platform in its own container, isolated from the rest of your machine. It is the only thing you install for this course.

- **macOS:** install [Docker Desktop](https://docs.docker.com/desktop/setup/install/mac-install/).
- **Linux:** install [Docker Engine](https://docs.docker.com/engine/install/), then follow the [post-installation steps](https://docs.docker.com/engine/install/linux-postinstall/) so you can run `docker` without `sudo`.
- **Windows:** see the next section.

If you have never used Docker, the first two parts of Docker's own [getting started guide](https://docs.docker.com/get-started/) are enough background. You will not write Docker files in this module, only run commands.

### Windows: set up WSL2 first

The course runs on Windows through WSL2, which gives you a real Linux environment inside Windows.

1. Open PowerShell as administrator and run `wsl --install`. Restart when asked. This installs Ubuntu.
2. Install [Docker Desktop](https://docs.docker.com/desktop/setup/install/windows-install/) and keep the option to use WSL2 selected.
3. In Docker Desktop, open Settings, then Resources, then WSL integration, and turn it on for Ubuntu.
4. Open the Ubuntu terminal. Do everything in this course from there.

**Clone the repository inside Linux, not on the Windows drive.** Use a folder such as `~/code`, not one under `/mnt/c`. Files on the Windows drive are much slower from WSL2 and can get the wrong line endings, which breaks the scripts.

### Give Docker enough memory

On macOS and Windows, Docker Desktop only uses the memory you allow it. Open Settings, then Resources, and set memory to at least 4 GB. If your machine has 16 GB, set 8 GB.

On Linux, Docker uses the machine's memory directly and there is nothing to set.

## 4. The course command

You control the environment with one command, `./course`, run from the repository folder.

| Command | What it does |
| --- | --- |
| `./course doctor` | Checks that Docker is installed, running and has enough memory |
| `./course up` | Starts the services |
| `./course status` | Shows each service and whether it is healthy |
| `./course data` | Downloads the datasets |
| `./course check 0` | Runs this module's checkpoint |
| `./course run <command>` | Runs a command in the toolbox |
| `./course shell` | Opens a shell in the toolbox |
| `./course down` | Stops everything |
| `./course help` | Lists the commands |

`./course` is a short script. It calls Docker Compose, the tool that starts several containers together from one description file. That description is [`compose.yaml`](../../compose.yaml) at the root of the repository. You do not need to understand it yet, but it is worth a look: every service you start in this course is declared there.

## 5. Lab

Go to [`lab/README.md`](lab/README.md) and follow it from start to finish. It takes you from cloning the repository to a passing checkpoint.

## 6. Exercise

When the lab is done, do the exercise in [`exercise/README.md`](exercise/README.md). You upload one of the IMDb files to the object storage with a few lines of Python.

A reference solution is in [`solution/`](solution/). Try the exercise before you open it.

## 7. In production

Your laptop setup is a small model of a real platform. The ideas are the same; the scale and the stakes are different.

| On your laptop | In a company |
| --- | --- |
| RustFS in a container | A cloud object storage such as Amazon S3, Google Cloud Storage or Azure Blob Storage. Nobody runs their own unless they must |
| One container per tool, started by Docker Compose | Managed cloud services, or containers run by an orchestrator such as Kubernetes across many machines |
| Credentials in a `.env` file | A secrets manager. Credentials are never in files that people copy around |
| `./course data`, run by hand | Ingestion jobs that run on a schedule and are monitored. You build these in modules 3 and 7 |
| `./course check 0` | Automated tests that run on every change. You build these in module 8 |
| A few gigabytes of data | Terabytes or more, where a careless query costs real money |

One thing does not change: object storage is the foundation. Almost every modern data platform keeps its data in one, which is why you start here.

## 8. Troubleshooting

Start with `./course doctor`. It catches the most common problems and says what to do.

**"Docker is installed but not running"**
Start Docker Desktop and wait until it says it is running. On Linux: `sudo systemctl start docker`.

**`./course: Permission denied`**
The script lost its executable flag. Run `chmod +x course`, or call it as `bash course up`.

**`bad interpreter` or `$'\r': command not found`**
The files have Windows line endings. This happens when the repository is cloned on the Windows drive. Clone it again inside WSL2, in a folder under your Linux home.

**"The services did not become healthy within 3 minutes"**
Run `./course status` to see which service is not healthy. The usual cause is that port 9000 or 9001 is already used by another program. Find it with `docker ps`, or stop the other program, then run `./course up` again.

**The download stops or is very slow**
Run `./course data` again. Files that finished are skipped; only the interrupted one starts over. The largest file is about 750 MB.

**"Docker has about N GiB of memory"**
Raise the memory limit in Docker Desktop, under Settings, then Resources. See [Give Docker enough memory](#give-docker-enough-memory).

**Starting over**
`./course down --wipe` stops everything and deletes what is stored in the object storage. Your downloaded datasets in `data/` are kept.
