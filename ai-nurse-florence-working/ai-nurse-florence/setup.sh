#!/usr/bin/env bash
set -euo pipefail

# Minimal reproducible setup for the ai-nurse-florence project
# Usage: ./setup.sh [--venv-dir .venv]

VENV_DIR=".venv"
if [[ ${1:-} == "--venv-dir" ]]; then
  VENV_DIR="$2"
fi

python3 -m venv "$VENV_DIR"
# shellcheck disable=SC1091
source "$VENV_DIR/bin/activate"

pip install --upgrade pip
if [[ -f requirements.txt ]]; then
  pip install -r requirements.txt
fi
if [[ -f requirements-dev.txt ]]; then
  pip install -r requirements-dev.txt
fi

echo "Setup complete. Activate with: source $VENV_DIR/bin/activate"
