#!/bin/bash
set -e

source ./gh-login.sh

LOG_DIR="/tmp/"
RUNNER_LOG="$LOG_DIR/runner_output.log"
CONTAINER_NAME=$(cat /etc/hostname)
LABELS="self-hosted,Linux,X64"

echo "Creating log file at '$RUNNER_LOG'..."

touch $RUNNER_LOG
chmod 644 $RUNNER_LOG

echo "The log file permissions for '$RUNNER_LOG' have been updated to 644, allowing everyone to read it."

if [ "$#" -ne 3 ]; then
    echo "Usage: $0 <REPO_URL> <GITHUB_TOKEN> <EXTRA_LABELS>"
    exit 1
fi

REPO_URL=$1
GH_TOKEN=$2
EXTRA_LABELS="$3"

if [[ -n "$EXTRA_LABELS" ]]; then
  LABELS="$LABELS,$EXTRA_LABELS"
fi

RUNNER_TOKEN=$(get_github_runner_token "$REPO_URL" "$GH_TOKEN")


if [[ -z "$RUNNER_TOKEN" ]]; then
    echo "Error: Could not obtain the authentication token."
    exit 1
fi

echo "Checking if the runner is already configured..."
if [ -f .runner ]; then
  echo "Runner is already configured. Skipping configuration."
else
  echo "Configuring the GitHub Actions Runner..."

  ./config.sh --url "$REPO_URL" --token "$RUNNER_TOKEN" --ephemeral --labels "$LABELS"
fi

echo "Starting the runner..."
Y | ./run.sh > "$RUNNER_LOG" 2>&1 &
runner_pid=$!

wait $runner_pid
