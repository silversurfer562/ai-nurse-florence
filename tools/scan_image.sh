#!/usr/bin/env bash
# Scan a local Docker image for vulnerabilities using trivy (preferred).
# Usage: ./tools/scan_image.sh <image:tag>

set -euo pipefail

IMAGE=${1:-localhost/ai-nurse-florence:latest}

if command -v trivy >/dev/null 2>&1; then
  echo "Running trivy scan on $IMAGE (CRITICAL,HIGH,MEDIUM)..."
  trivy image --severity CRITICAL,HIGH,MEDIUM --no-progress "$IMAGE"
  exit 0
fi

if command -v docker >/dev/null 2>&1; then
  echo "trivy not found. You can install trivy (https://aquasecurity.github.io/trivy/)"
  echo "Alternatively, if you have Docker's built-in scan support, run: docker scan $IMAGE"
  exit 2
fi

echo "No suitable scanner found. Install trivy or use Docker Desktop's Vulnerability Scanning."
exit 3
