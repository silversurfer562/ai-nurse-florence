FROM python:3.11-slim

WORKDIR /app

# Install system dependencies including Node.js for frontend build
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    nodejs \
    npm \
    && rm -rf /var/lib/apt/lists/*

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on

# Install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --break-system-packages --no-cache-dir -r requirements.txt

# Create non-root user
RUN useradd --create-home --shell /bin/bash florence

# Copy application files (bust cache: 2025-10-06-00:52-medication-card-fix)
COPY . /app

# Build frontend on Railway - force fresh build for MedicationCard component
WORKDIR /app/frontend
RUN npm ci && npm run build

# Back to app directory
WORKDIR /app

# Create data directory for persistent database storage
# Note: Railway volume will be mounted here, so we don't build DB in Dockerfile
# Database will be built on first run via start-railway.sh if not present
RUN mkdir -p /app/data && chown -R florence:florence /app

# Make the startup script executable
RUN chmod +x /app/start-railway.sh

USER florence

# Expose application port - Railway uses 8080 by default
EXPOSE 8080

# Default command: use our startup script that handles PORT properly
CMD ["/app/start-railway.sh"]
