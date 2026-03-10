FROM python:3.13-slim

WORKDIR /app

COPY pyproject.toml ./
COPY codexapi/ ./codexapi/

RUN pip install --no-cache-dir -e .

EXPOSE 8000
