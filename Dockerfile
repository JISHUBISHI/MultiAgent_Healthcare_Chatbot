# syntax=docker/dockerfile:1

# ---------------------------------------------------------------------------
# Stage 1: Build — install dependencies
# ---------------------------------------------------------------------------
FROM python:3.11-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Install system-level build tools (needed by some Python packages)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        gcc \
        ca-certificates \
        curl && \
    rm -rf /var/lib/apt/lists/*

# Install Python dependencies into an isolated prefix so we can copy them cleanly
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --prefix=/install -r requirements.txt

# ---------------------------------------------------------------------------
# Stage 2: Runtime — lean production image
# ---------------------------------------------------------------------------
FROM python:3.11-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    # Default port — Render will override this at runtime via $PORT
    PORT=10000

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        ca-certificates && \
    rm -rf /var/lib/apt/lists/*

# Copy installed packages from the builder stage
COPY --from=builder /install /usr/local

# Copy only the files the app actually needs at runtime
# (secrets / .env should be injected via Render's environment variables, NOT baked in)
COPY agents.py \
     app.py \
     config.py \
     pdf_generator.py \
     table_format.py \
     web_app.py \
     wsgi.py \
     index.html \
     manifest.webmanifest \
     service-worker.js \
     healthbuddy-app.ico \
     healthbuddy-logo.jpeg \
     icon-192.png \
     icon-512.png \
     icon-512-maskable.png \
     requirements.txt \
     ./

# Create a non-root user for security
RUN useradd --no-create-home --shell /bin/false appuser && \
    chown -R appuser /app
USER appuser

# Expose the port Gunicorn will listen on
EXPOSE ${PORT}

# Render passes $PORT at runtime; Gunicorn reads it via the shell before starting
CMD gunicorn --bind "0.0.0.0:${PORT}" \
             --workers 2 \
             --threads 2 \
             --timeout 120 \
             --access-logfile - \
             --error-logfile - \
             wsgi:app
