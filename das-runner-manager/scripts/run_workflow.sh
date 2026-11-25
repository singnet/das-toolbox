#!/bin/bash
set -e

GITHUB_REPO_NAME="${1:-singnet/das}"
WORKFLOW_NAME="${2:-check-repos.yml}"

if [ -f ".authtoken~" ] && [ -s ".authtoken~" ]; then
    gh auth login --with-token < .authtoken~
    GH_CALL_OUTPUT=$(gh workflow run $WORKFLOW_NAME --ref master --repo $GITHUB_REPO_NAME)

    echo "[$(date)] : $GH_CALL_OUTPUT" >> /root/logs/run_workflow.logs
else
    echo "[ERROR]: Was not able to authenticate to github, '.authtoken~' file is missing or is empty."
fi