#!/bin/bash
set -e

LOG_DIR="/tmp/"
RUNNER_LOG="$LOG_DIR/runner_output.log"

CONTAINER_NAME=$(cat /etc/hostname)

if [ ! -f "$RUNNER_LOG" ]; then
    echo "Log file not found at $RUNNER_LOG"
    exit 1
fi

echo "Monitoring the runner log file..."

tail -f "$RUNNER_LOG" | while read line; do
    if [[ "$line" == *"completed"* ]]; then
        echo "Job completed."

        if grep -q "Job succeeded" "$RUNNER_LOG"; then
            echo "Job succeeded."
        elif grep -q "Job failed" "$RUNNER_LOG"; then
            echo "Job failed."
        fi

        echo "Initiating restart sequence for container $CONTAINER_NAME..."
        curl -X POST "http://das-runner-manager-agent:3000/containers/$CONTAINER_NAME/restart-sequence" || true

        break
    fi
done
