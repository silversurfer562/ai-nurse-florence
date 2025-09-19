#!/bin/bash
set -e  # Exit on any error

# Get the current branch name
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)

echo "Working on branch: $CURRENT_BRANCH"

# Check if there are any changes to commit
if git diff-index --quiet HEAD --; then
    echo "No changes to commit."
    exit 0
fi

# Add all changes
echo "Adding changes..."
git add .

# Commit with a message (can be customized via first argument)
COMMIT_MSG="${1:-update: latest changes}"
echo "Committing with message: $COMMIT_MSG"
git commit -m "$COMMIT_MSG"

# Pull latest changes with rebase
echo "Pulling latest changes from origin/$CURRENT_BRANCH..."
if git pull --rebase origin "$CURRENT_BRANCH"; then
    echo "Successfully rebased."
else
    echo "Warning: Could not pull from origin/$CURRENT_BRANCH. This might be a new branch."
fi

# Push to the current branch
echo "Pushing to origin/$CURRENT_BRANCH..."
git push origin "$CURRENT_BRANCH"

echo "Successfully updated $CURRENT_BRANCH!"
