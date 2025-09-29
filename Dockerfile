### Builder stage: create a virtualenv and install dependencies
FROM python:3.11.13-slim AS builder
WORKDIR /install

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    ca-certificates \
    curl \
    && rm -rf /var/lib/apt/lists/*

ENV VENV_PATH=/opt/venv
RUN python -m venv $VENV_PATH
ENV PATH="$VENV_PATH/bin:$PATH"

# Copy and install python deps into the virtualenv
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

### Final image: copy virtualenv and application, run as non-root user
FROM python:3.11.13-slim
ENV VENV_PATH=/opt/venv
COPY --from=builder $VENV_PATH $VENV_PATH
ENV PATH="$VENV_PATH/bin:$PATH"

WORKDIR /app

# Add a non-root user for security
RUN useradd --create-home --shell /bin/bash --uid 1000 florence || true

# Copy application files
COPY . /app
RUN chown -R florence:florence /app

USER florence

# Expose application port
EXPOSE 8000

# Default command: production Gunicorn with Uvicorn workers
# The PORT environment variable is honored by Docker/hosting platforms
CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "--workers", "4", "--bind", "0.0.0.0:${PORT:-8000}", "app:app"]
