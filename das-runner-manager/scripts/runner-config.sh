#!/usr/bin/env bash

# Simple defaults for batch runner provisioning.
# Add/remove entries in the arrays below as needed.

GITHUB_ORG="singnet"

REPOSITORIES=(
  "das"
  "das-toolbox"
)

USERS=(
  "levisingularity"
  "marcocapozzoli"
  "andre-senna"
  "arturgontijo"
)

# Number of no-cache runners to create per selected repository.
NO_CACHE_RUNNERS=2
