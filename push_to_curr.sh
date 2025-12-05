#!/bin/bash

# Default commit message
COMMIT_MESSAGE="cuh"

# Check if a commit message is provided as an argument
if [ -n "$1" ]; then
  COMMIT_MESSAGE="$1"
fi

# Stage all changes
git add .

# Commit changes
git commit -m "$COMMIT_MESSAGE"

# Get current branch name
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)

# Push to origin
git push origin "$CURRENT_BRANCH"
