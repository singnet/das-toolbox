#!/bin/bash
set -e

source ./gh-login.sh

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

echo "Configuring the GitHub Actions Runner..."
./config.sh --url "$REPO_URL" --token "$RUNNER_TOKEN"

echo "Starting the runner..."
./run.sh &
runner_pid=$!

wait $runner_pid
