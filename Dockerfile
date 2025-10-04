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

# Copy application files (bust cache: 2025-10-04-11:00-frontend-rebuild)
COPY . /app

# Build frontend on Railway
WORKDIR /app/frontend
RUN npm ci && npm run build

# Back to app directory
WORKDIR /app

# Build drug database from FDA (production data)
RUN python3 scripts/build_drug_database.py --max-records 25000 || echo "Drug database build failed, will use FDA API fallback"

RUN chown -R florence:florence /app

# Make the startup script executable
RUN chmod +x /app/start-railway.sh

USER florence

# Expose application port - Railway uses 8080 by default
EXPOSE 8080

# Default command: use our startup script that handles PORT properly
CMD ["/app/start-railway.sh"]
