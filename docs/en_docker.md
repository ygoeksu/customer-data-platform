# Docker

## What is Docker?

Docker is a platform that packages an application together with everything it needs to run — code, runtime, dependencies, environment variables, and config — into a single unit called a **container**.

A container is isolated from the host system and from other containers. This solves the classic "works on my machine" problem: if it runs in the container, it runs anywhere Docker is installed.

Key concepts:

| Term | Description |
|---|---|
| **Image** | A read-only blueprint for a container (like a class) |
| **Container** | A running instance of an image (like an object) |
| **Dockerfile** | A text file with instructions to build an image |
| **Registry** | A storage service for images (e.g. Docker Hub) |
| **Volume** | A way to mount host directories into a container |

---

## Where to get images

### Docker Hub — [hub.docker.com](https://hub.docker.com)

The default public registry. Images are pulled from here automatically when you run `docker pull <name>`.

```bash
docker pull python:3.14-slim     # official Python image
docker pull postgres:17          # official PostgreSQL image
```

**Official images** (maintained by the software vendors) are marked with a blue badge. Prefer these over community images for base images.

**Image tags** control the version:
- `python:3.14-slim` — specific version, minimal OS (recommended for production)
- `python:latest` — always the newest release (unpredictable, avoid in production)
- `python:3.14` — full Debian image, much larger

### GitHub Container Registry — `ghcr.io`

Used by open-source projects that host their own images alongside their code.

```bash
# Example: uv (the Python package manager)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/
```

### Other registries

| Registry | URL | Common use |
|---|---|---|
| AWS ECR | `<account>.dkr.ecr.<region>.amazonaws.com` | Private images on AWS |
| Google Artifact Registry | `<region>-docker.pkg.dev` | Private images on GCP |
| Azure Container Registry | `<name>.azurecr.io` | Private images on Azure |

For production ETL pipelines, teams typically push their custom images to a private registry to control versioning and access.

---

## Docker in ETL pipelines

Docker is widely used in ETL because pipelines have strict environment requirements (exact Python version, specific library versions, OS-level dependencies) and need to run reliably across local machines, CI/CD systems, and cloud schedulers.

### Pattern 1: Containerized pipeline script

The simplest pattern — package the entire pipeline as one image, run it on a schedule.

```
Scheduler (cron / Airflow / Prefect)
    └── docker run customer-data-platform
            └── extract → validate → transform → load
```

This is what this project does. The container runs `main.py`, finishes, and exits.

```bash
docker run --rm -v ./data:/app/data customer-data-platform
```

### Pattern 2: One container per stage

Each ETL stage runs in its own container. Useful when stages have conflicting dependencies or need to scale independently.

```
Extract container  →  (writes to S3 / shared volume)
Transform container  →  (reads from S3, writes result)
Load container  →  (reads result, writes to DB)
```

Orchestrators like Apache Airflow or Prefect manage the dependencies between stages using `DockerOperator` or similar task types.

### Pattern 3: Containers in orchestration platforms

In larger setups, containers run inside Kubernetes (K8s) or a managed service:

| Platform | Description |
|---|---|
| **Kubernetes + CronJob** | Schedule containers on a cluster |
| **AWS ECS / Fargate** | Run containers without managing servers |
| **Google Cloud Run Jobs** | Serverless container execution |
| **Azure Container Instances** | Simple on-demand container runs |

These platforms handle scaling, retries, and logging — the pipeline code stays unchanged since it's just a container.

### Why Docker fits ETL well

- **Reproducibility** — the same image runs in dev, staging, and production
- **Isolation** — different pipelines can use different Python versions without conflict
- **Portability** — switch cloud providers without rewriting the pipeline
- **Versioning** — images are tagged, so rollbacks are a one-line change
- **Dependency freeze** — `uv pip install .` at build time captures exact package versions in the image layer

---

## Common commands

```bash
# Build an image from the Dockerfile in the current directory
docker build -t my-pipeline .

# Run a container (--rm removes it after it exits)
docker run --rm my-pipeline

# Mount a local directory into the container
docker run --rm -v ./data:/app/data my-pipeline

# Pass environment variables
docker run --rm -e DB_URL=sqlite:///app/db.sqlite my-pipeline

# List running containers
docker ps

# List all images
docker images

# Remove an image
docker rmi my-pipeline
```
