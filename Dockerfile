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
    pip install -r requirements.txt

# Copy application code
COPY . .

# Expose the application port
EXPOSE 8000

# Health check - let Railway handle this with its own health check
# CMD will use the proper PORT environment variable at runtime

# Ensure start script exists and is executable (uses $PORT on Railway)
COPY run.sh .
RUN chmod +x run.sh

# Command to run the application - binds to $PORT provided by Railway
CMD ["./run.sh"]