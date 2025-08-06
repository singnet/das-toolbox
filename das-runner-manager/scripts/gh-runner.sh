#!/bin/bash
set -e

source ./gh-login.sh

LOG_DIR="/tmp/"
RUNNER_LOG="$LOG_DIR/runner_output.log"
EXTRA_LABELS=$(docker inspect --format '{{range $k,$v := .Config.Labels}}{{printf "%s," $k}}{{end}}' "$CONTAINER_NAME" | sed 's/,$//')
LABELS="self-hosted,Linux,X64"

if [[ -n "$EXTRA_LABELS" ]]; then
  LABELS="$LABELS,$EXTRA_LABELS"
fi

echo "Creating log file at '$RUNNER_LOG'..."

touch $RUNNER_LOG
chmod 644 $RUNNER_LOG

echo "The log file permissions for '$RUNNER_LOG' have been updated to 644, allowing everyone to read it."

if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <REPO_URL> <GITHUB_TOKEN>"
    exit 1
fi

REPO_URL=$1
GH_TOKEN=$2
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
