#!/usr/bin/env bash
# scripts/sync_env_to_vercel.sh
# Safely sync .env.vercel to Vercel project environment variables using the Vercel CLI.
# - Skips blank values
# - Prompts before adding or updating each variable
# - Requires `vercel` CLI to be logged in and the project selected
# Usage: ./scripts/sync_env_to_vercel.sh [path-to-env-file] [environment]
# environment: production | preview | development (default: preview)

set -euo pipefail

ENV_FILE=${1:-.env.vercel}
ENV_SCOPE=${2:-preview}

if ! command -v vercel >/dev/null 2>&1; then
  echo "vercel CLI not found. Install it: npm i -g vercel"
  exit 1
fi

if [ ! -f "$ENV_FILE" ]; then
  echo "Env file not found: $ENV_FILE"
  exit 1
fi

echo "Reading env file: $ENV_FILE"

action_confirm() {
  # prompt user to confirm action
  read -r -p "$1 [y/N]: " resp
  case "$resp" in
    [yY][eE][sS]|[yY]) return 0 ;;
    *) return 1 ;;
  esac
}

# Parse file line-by-line, ignore comments and blank lines
while IFS= read -r line || [ -n "$line" ]; do
  # trim whitespace
  key=$(echo "$line" | sed -E 's/^\s+|\s+$//g')
  # skip comments and empty
  if [[ -z "$key" || "$key" =~ ^# ]]; then
    continue
  fi
  # only handle KEY=VALUE pairs
  if ! echo "$key" | grep -q '='; then
    echo "Skipping non KEY=VALUE line: $key"
    continue
  fi
  VAR_NAME=$(echo "$key" | cut -d'=' -f1)
  VAR_VALUE=$(echo "$key" | cut -d'=' -f2-)

  # skip variables with empty value
  if [[ -z "$VAR_VALUE" ]]; then
    echo "Skipping $VAR_NAME - value is empty"
    continue
  fi

  echo "\nPreparing to add/update: $VAR_NAME (env: $ENV_SCOPE)"
  if action_confirm "Proceed to add/update $VAR_NAME in Vercel?"; then
    # Use vercel env add in non-interactive manner via echo
    # Vercel CLI requires specifying environment; use 'production', 'preview', or 'development'
    # To update an existing variable, remove then add (vercel currently has add/update semantics per env)
    echo "$VAR_VALUE" | vercel env add "$VAR_NAME" "$ENV_SCOPE" --yes || {
      echo "Failed to add $VAR_NAME directly; attempting to remove and re-add..."
      vercel env rm "$VAR_NAME" "$ENV_SCOPE" --yes || true
      echo "$VAR_VALUE" | vercel env add "$VAR_NAME" "$ENV_SCOPE" --yes
    }
    echo "Added/Updated $VAR_NAME"
  else
    echo "Skipped $VAR_NAME"
  fi

done < <(grep -v '^\s*#' "$ENV_FILE" | sed '/^\s*$/d')

echo "\nCompleted syncing envs to Vercel (scope: $ENV_SCOPE)."

echo "Remember: secrets are sensitive. Avoid committing .env files with real secrets to the repository." 
