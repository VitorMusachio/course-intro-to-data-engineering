# Toolbox: the Python environment that runs module checkpoints and course
# scripts, so learners need nothing installed besides Docker.
FROM python:3.15-slim

COPY --from=ghcr.io/astral-sh/uv:0.5.11 /uv /usr/local/bin/uv

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_SYSTEM_PYTHON=1 \
    UV_NO_CACHE=1

COPY requirements.txt /tmp/requirements.txt
RUN uv pip install --requirement /tmp/requirements.txt \
    && rm /tmp/requirements.txt

WORKDIR /course

CMD ["python", "--version"]
