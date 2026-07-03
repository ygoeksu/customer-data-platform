FROM python:3.14-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

COPY pyproject.toml .

RUN uv pip install --system --no-cache .

COPY . .

ENV PYTHONPATH=/app/src

CMD ["python", "main.py"]
