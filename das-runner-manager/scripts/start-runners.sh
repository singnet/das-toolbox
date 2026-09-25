#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
RUNNER_MANAGER_BIN="${PROJECT_DIR}/dist/das-runner-manager"

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

wait_for_agent_health() {
  local max_attempts=24
  local attempt=1

  while [[ "$attempt" -le "$max_attempts" ]]; do
    if curl -fsS "http://localhost:3000/health" >/dev/null 2>&1; then
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
  run_cli start-agent
}

start_user_cache_runners() {
  local arch_labels_csv
  arch_labels_csv="$(IFS=,; echo "${ARCH_LABELS[*]}")"

  for user in "${USERS[@]}"; do
    local runner_name
    runner_name="${SELECTED_REPO}-github-runner-${user}"

    local labels_csv
    labels_csv="${arch_labels_csv},${user}"

    echo "Starting cache runner '${runner_name}' for user '${user}'..."
    GH_TOKEN="$GH_TOKEN" run_cli start \
      --org "$GITHUB_ORG" \
      --repository "$SELECTED_REPO" \
      --runners 1 \
      --labels "$labels_csv" \
      --runner-name "$runner_name"
  done
}

start_nocache_runners() {
  local arch_labels_csv
  arch_labels_csv="$(IFS=,; echo "${ARCH_LABELS[*]}")"

  echo "Starting ${NO_CACHE_RUNNERS} no-cache runners for '${SELECTED_REPO}'..."
  GH_TOKEN="$GH_TOKEN" run_cli start \
    --org "$GITHUB_ORG" \
    --repository "$SELECTED_REPO" \
    --runners "$NO_CACHE_RUNNERS" \
    --no-cache-runners "$NO_CACHE_RUNNERS" \
    --labels "$arch_labels_csv"
}

main() {
  require_command curl

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

  read -r -s -p "Enter GitHub Token: " GH_TOKEN
  echo

  if [[ -z "$GH_TOKEN" ]]; then
    echo "Error: GitHub token is required."
    exit 1
  fi

  detect_arch_labels

  echo "Repository selected: ${SELECTED_REPO}"
  echo "Architecture labels: $(IFS=,; echo "${ARCH_LABELS[*]}")"

  start_agent
  wait_for_agent_health
  start_user_cache_runners
  start_nocache_runners

  echo "Done: runners started for repository '${SELECTED_REPO}'."
}

main "$@"
