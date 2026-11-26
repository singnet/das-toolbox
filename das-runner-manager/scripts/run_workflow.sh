#!/bin/bash
set -e

GITHUB_REPO_NAME="${1:-singnet/das}"
WORKFLOW_NAME="${2:-check-repos.yml}"

if [[ ! -d "$HOME/logs" ]]; then
    mkdir -p "$HOME/logs"
fi

if [ -f ".authtoken~" ] && [ -s ".authtoken~" ]; then
    gh auth login --with-token < .authtoken~
    gh workflow run "$WORKFLOW_NAME" --ref master --repo "$GITHUB_REPO_NAME"

    echo "[$(date)] -> Successfully called workflow "$WORKFLOW_NAME" at "$GITHUB_REPO_NAME"" >> /$HOME/logs/run_workflow.logs
else
    echo "[ERROR]: Was not able to authenticate to github, '.authtoken~' file is missing or is empty."
    exit 1
fi