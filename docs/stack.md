# Stack

Every tool the course uses, what it is for, and the file where its version is pinned.

The pin in that file is the single source of truth. Versions are not repeated here, because they are updated often: Dependabot opens a pull request when a newer release exists, and the checkpoints in CI decide whether the update is safe.

To see the versions you are running:

```
./course run python --version
./course run pip list
docker compose --profile base images
```

| Tool | Used for | Introduced in | Version pinned in |
| --- | --- | --- | --- |
| RustFS | Local S3-compatible object storage | Module 0 | `compose.yaml` |
| Python | Toolbox image: checkpoints and scripts | Module 0 | `docker/toolbox/Dockerfile` |
| uv | Installing Python packages in the toolbox | Module 0 | `docker/toolbox/Dockerfile` |
| pytest | Module checkpoints | Module 0 | `docker/toolbox/requirements.txt` |
| boto3 | S3 client used by checkpoints and scripts | Module 0 | `docker/toolbox/requirements.txt` |
| PyYAML | Reading `config/sources.yml` | Module 0 | `docker/toolbox/requirements.txt` |

Why each tool was chosen is recorded in `docs/decisions/` when there was a real choice to make.
