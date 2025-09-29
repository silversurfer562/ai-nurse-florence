FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on

# Install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && \
# Copy application files
COPY . /app
RUN chown -R florence:florence /app

# Make the startup script executable
RUN chmod +x /app/start-railway.sh

USER florence

# Expose application port
EXPOSE 8000

# Default command: use our startup script that handles PORT properly
CMD ["/app/start-railway.sh"]