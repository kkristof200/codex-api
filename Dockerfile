FROM python:3.13-slim

RUN pip install uv

WORKDIR /app

COPY pyproject.toml ./
COPY packages/ ./packages/

RUN uv sync --no-dev

ENV PATH="/app/.venv/bin:$PATH"

EXPOSE 8000
