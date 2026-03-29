# syntax=docker/dockerfile:1

FROM python:3.11-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=on \
    POETRY_VIRTUALENVS_CREATE=false

WORKDIR /app

# Install system dependencies required by popular Python packages
RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential gcc curl && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

COPY . ./

# Create non-root user
RUN useradd --create-home appuser && \
    chown -R appuser /app
USER appuser

EXPOSE 8501

ENTRYPOINT ["gunicorn", "--bind", "0.0.0.0:8501", "wsgi:app"]