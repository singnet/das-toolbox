#!/bin/bash
set -e

source ./gh-login.sh

USERID=$(id -u "$USER")
GROUPID=$(id -g "$USER")

cleanup() {
   pkill -9 dockerd

   RUNNER_TOKEN=$(get_github_runner_token "$REPO_URL" "$GH_TOKEN")

    echo "Removing the GitHub Actions runner..."
    sudo -u "$USER" ./config.sh remove --token "$RUNNER_TOKEN" || true
}

trap cleanup SIGINT SIGTERM EXIT

echo "Running as user: $(whoami) on host: $(hostname)"

echo "Configuring permissions for the cache folder at /home/$USER/.cache..."
echo "Current user: $USER, User ID: $USERID, Group ID: $GROUPID"

chown "$USERID:$GROUPID" "/home/$USER/.cache" -R

if docker info > /dev/null 2>&1; then
    echo "Docker is already running."
else
    echo "Starting dockerd..."
    
    if [ -f /var/run/docker.pid ]; then
        echo "Removing stale Docker PID file..."
        rm -f /var/run/docker.pid
    fi

    dockerd &
    sleep 10

    if ! docker info > /dev/null 2>&1; then
        echo "ERROR: Docker is not running!"
        cat /var/log/dockerd.log
        exit 1
    fi
fi

echo "Setting permissions for Docker socket..."
chmod 777 /var/run/docker.sock

sudo -u "$USER" ./gh-runner.sh "$REPO_URL" "$GH_TOKEN" &
RUNNER_PID=$!

sleep 10s

echo "Starting GitHub Runner log monitoring..."
./monitor_runner_log.sh &

wait $RUNNER_PID
