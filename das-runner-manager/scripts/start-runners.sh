#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
RUNNER_MANAGER_BIN="${PROJECT_DIR}/dist/das-runner-manager"
AGENT_START_TIMEOUT_SECONDS=180
CREATED_RUNNERS=()
STARTUP_IN_PROGRESS=0

source "${SCRIPT_DIR}/runner-config.sh"

require_command() {
  local cmd="$1"
  if ! command -v "$cmd" >/dev/null 2>&1; then
    echo "Error: command '$cmd' not found."
    exit 1
  fi
}

run_cli() {
  "$RUNNER_MANAGER_BIN" "$@"
}

runner_exists() {
  local runner_name="$1"
  docker ps -a --format '{{.Names}}' --filter "name=^${runner_name}$" | grep -Fxq "$runner_name"
}

cleanup_created_runners() {
  if [[ "${#CREATED_RUNNERS[@]}" -eq 0 ]]; then
    return
  fi

  echo "Cleaning up runners created in this execution..."
  set +e
  for runner_name in "${CREATED_RUNNERS[@]}"; do
    if runner_exists "$runner_name"; then
      echo "Removing runner container '${runner_name}'..."
      docker rm -f "$runner_name" >/dev/null 2>&1 || true
    fi
  done
  set -e
}

on_startup_error() {
  local exit_code=$?
  if (( STARTUP_IN_PROGRESS == 1 )); then
    cleanup_created_runners
  fi
  exit "$exit_code"
}

wait_for_agent_health() {
  local max_attempts=24
  local attempt=1

  while [[ "$attempt" -le "$max_attempts" ]]; do
    if curl -fsS --connect-timeout 2 --max-time 4 "http://localhost:3000/health" >/dev/null 2>&1; then
      echo "Agent is healthy."
      return 0
    fi

    echo "Waiting for agent health (${attempt}/${max_attempts})..."
    sleep 5
    attempt=$((attempt + 1))
  done

  echo "Error: agent health check timed out on http://localhost:3000/health"
  exit 1
}

select_repository() {
  echo "Select repository:"
  local i=1
  for repo in "${REPOSITORIES[@]}"; do
    echo "  ${i}) ${repo}"
    i=$((i + 1))
  done

  local choice
  read -r -p "Enter option number: " choice

  if ! [[ "$choice" =~ ^[0-9]+$ ]]; then
    echo "Error: invalid option '${choice}'."
    exit 1
  fi

  if (( choice < 1 || choice > ${#REPOSITORIES[@]} )); then
    echo "Error: option out of range."
    exit 1
  fi

  SELECTED_REPO="${REPOSITORIES[$((choice - 1))]}"
}

detect_arch_labels() {
  local machine
  machine="$(uname -m)"

  case "$machine" in
    x86_64|amd64)
      ARCH_LABELS=("amd64" "amd")
      ;;
    aarch64|arm64)
      ARCH_LABELS=("arm64" "arm")
      ;;
    *)
      echo "Error: unsupported architecture '${machine}'."
      exit 1
      ;;
  esac
}

start_agent() {
  echo "Starting agent container..."
  set +e
  timeout "${AGENT_START_TIMEOUT_SECONDS}" run_cli start-agent
  local status=$?
  set -e

  if [[ "$status" -eq 124 ]]; then
    echo "Error: start-agent exceeded ${AGENT_START_TIMEOUT_SECONDS}s timeout."
  fi
  return "$status"
}

start_user_cache_runners() {
  local arch_labels_csv
  arch_labels_csv="$(IFS=,; echo "${ARCH_LABELS[*]}")"

  for user in "${USERS[@]}"; do
    local runner_name
    runner_name="${SELECTED_REPO}-github-runner-${user}"

    local labels_csv
    labels_csv="${arch_labels_csv},${user}"

    if runner_exists "$runner_name"; then
      echo "Skipping cache runner '${runner_name}' because it already exists."
      continue
    fi

    echo "Starting cache runner '${runner_name}' for user '${user}'..."
    GH_TOKEN="$GH_TOKEN" run_cli start \
      --org "$GITHUB_ORG" \
      --repository "$SELECTED_REPO" \
      --runners 1 \
      --labels "$labels_csv" \
      --runner-name "$runner_name"

    CREATED_RUNNERS+=("$runner_name")
  done
}

start_nocache_runners() {
  local arch_labels_csv
  arch_labels_csv="$(IFS=,; echo "${ARCH_LABELS[*]}")"

  echo "Reconciling ${NO_CACHE_RUNNERS} no-cache runners for '${SELECTED_REPO}'..."
  for ((i = 0; i < NO_CACHE_RUNNERS; i++)); do
    local runner_name
    runner_name="${SELECTED_REPO}-github-runner-${i}"

    if runner_exists "$runner_name"; then
      echo "Skipping no-cache runner '${runner_name}' because it already exists."
      continue
    fi

    echo "Starting no-cache runner '${runner_name}'..."
    GH_TOKEN="$GH_TOKEN" run_cli start \
      --org "$GITHUB_ORG" \
      --repository "$SELECTED_REPO" \
      --runners 1 \
      --no-cache-runners 1 \
      --labels "$arch_labels_csv" \
      --runner-name "$runner_name"

    CREATED_RUNNERS+=("$runner_name")
  done
}

main() {
  require_command curl
  require_command docker
  require_command timeout

  if [[ ! -x "$RUNNER_MANAGER_BIN" ]]; then
    echo "Error: binary not found at '$RUNNER_MANAGER_BIN'."
    echo "Build it first from '$PROJECT_DIR' with:"
    echo "  make build"
    exit 1
  fi

  if [[ "${#REPOSITORIES[@]}" -eq 0 ]]; then
    echo "Error: no repositories configured."
    exit 1
  fi

  if [[ "${#USERS[@]}" -eq 0 ]]; then
    echo "Error: no users configured."
    exit 1
  fi

  select_repository

  if [[ -z "${GH_TOKEN:-}" ]]; then
    read -r -s -p "Enter GitHub Token: " GH_TOKEN
    echo
  fi

  if [[ -z "$GH_TOKEN" ]]; then
    echo "Error: GitHub token is required."
    exit 1
  fi

  detect_arch_labels

  if ! [[ "$NO_CACHE_RUNNERS" =~ ^[0-9]+$ ]]; then
    echo "Error: NO_CACHE_RUNNERS must be a non-negative integer."
    exit 1
  fi

  if (( NO_CACHE_RUNNERS > 15 )); then
    echo "Error: NO_CACHE_RUNNERS must be between 0 and 15."
    exit 1
  fi

  echo "Repository selected: ${SELECTED_REPO}"
  echo "Architecture labels: $(IFS=,; echo "${ARCH_LABELS[*]}")"

  STARTUP_IN_PROGRESS=1
  trap on_startup_error ERR

  start_agent
  wait_for_agent_health
  start_user_cache_runners
  if (( NO_CACHE_RUNNERS > 0 )); then
    start_nocache_runners
  else
    echo "Skipping no-cache runners because NO_CACHE_RUNNERS=0."
  fi

  STARTUP_IN_PROGRESS=0
  trap - ERR

  echo "Done: runners started for repository '${SELECTED_REPO}'."
}

main "$@"
