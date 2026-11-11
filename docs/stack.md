# Stack

Every tool the course uses, with the version it is pinned to. A module is not done until the tools it introduces are listed here.

| Tool | Version | Used for | Introduced in | Where it is pinned |
| --- | --- | --- | --- | --- |
| Python | 3.13 | Toolbox image: checkpoints and scripts | Module 0 | `docker/toolbox/Dockerfile` |
| uv | 0.5.11 | Installing Python packages in the toolbox | Module 0 | `docker/toolbox/Dockerfile` |
| pytest | 8.3.4 | Module checkpoints | Module 0 | `docker/toolbox/requirements.txt` |
| boto3 | 1.35.90 | S3 client used by checkpoints and scripts | Module 0 | `docker/toolbox/requirements.txt` |
| RustFS | 1.0.0 | Local S3-compatible object storage | Module 0 | `compose.yaml` (from T07) |

Versions are kept current by Dependabot, which opens a pull request when a newer release exists.
