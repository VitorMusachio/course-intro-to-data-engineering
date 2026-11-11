# Stack

Every tool the course uses, with the version it is pinned to. A module is not done until the tools it introduces are listed here.

| Tool | Version | Used for | Introduced in | Where it is pinned |
| --- | --- | --- | --- | --- |
| Python | 3.13 | Toolbox image: checkpoints and scripts | Module 0 | `docker/toolbox/Dockerfile` |
| uv | 0.5.11 | Installing Python packages in the toolbox | Module 0 | `docker/toolbox/Dockerfile` |
| pytest | 9.2.0 | Module checkpoints | Module 0 | `docker/toolbox/requirements.txt` |
| boto3 | 1.43.126 | S3 client used by checkpoints and scripts | Module 0 | `docker/toolbox/requirements.txt` |
| PyYAML | 6.0.2 | Reading `config/sources.yml` | Module 0 | `docker/toolbox/requirements.txt` |
| RustFS | 1.0.0 | Local S3-compatible object storage | Module 0 | `compose.yaml` |

Versions are kept current by Dependabot, which opens a pull request when a newer release exists.
