#!/bin/bash
set -e

check_github_auth() {
    local GH_TOKEN="$1"

    if ! gh auth status &>/dev/null; then
        echo "$GH_TOKEN" | gh auth login --with-token
    fi
}

get_github_runner_token() {
    local REPO_URL=$1
    local GH_TOKEN=$2
    local REPO_NAME RUNNER_TOKEN

    check_github_auth "$GH_TOKEN"

    ORG_NAME=$(echo "$REPO_URL" | sed 's|https://github.com/\([^/]*\)/.*|\1|')
    REPO_NAME=$(echo "$REPO_URL" | sed 's|https://github.com/[^/]*/\(.*\)|\1|')

    RUNNER_TOKEN=$(gh api --method POST -H "Accept: application/vnd.github+json" /repos/$ORG_NAME/$REPO_NAME/actions/runners/registration-token --jq '.token')

    echo "$RUNNER_TOKEN"
}