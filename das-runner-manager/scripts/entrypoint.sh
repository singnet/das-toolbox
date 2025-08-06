#!/bin/bash
set -e

source ./gh-login.sh

USERID=$(id -u "$USER")
GROUPID=$(id -g "$USER")

cleanup() {
   RUNNER_TOKEN=$(get_github_runner_token "$REPO_URL" "$GH_TOKEN")

    echo "Removing the GitHub Actions runner..."
    sudo -u "$USER" ./config.sh remove --token "$RUNNER_TOKEN" || true

    echo "Cleaning tmpfs directories..."
    for dir in "/var/lib/docker" "/tmp" "/var/tmp" "/var/cache" "/var/log" "/home/ubuntu"; do
        if [ -d "$dir" ]; then
            echo "Cleaning $dir..."
            sudo rm -rf "$dir"/*
        fi
    done
}

trap cleanup SIGINT SIGTERM EXIT

echo "Running as user: $(whoami) on host: $(hostname)"

if [ ! -d "/home/$USER" ]; then
    echo "Creating /home/$USER directory..."
    mkdir -p "/home/$USER"
fi

echo "Changing ownership of /home/$USER to $USER..."
sudo chown "$USERID:$GROUPID" "/home/$USER"

echo "Configuring permissions for the cache folder at /home/$USER/.cache..."
echo "Current user: $USER, User ID: $USERID, Group ID: $GROUPID"

if [ ! -d "/home/$USER/.cache" ]; then
    echo "Creating /home/$USER/.cache directory..."
    mkdir -p "/home/$USER/.cache"
fi

chown "$USERID:$GROUPID" "/home/$USER/.cache" -R

if docker info > /dev/null 2>&1; then
    echo "Docker is already running."
else
    echo "Starting dockerd..."
    
    if [ -f /var/run/docker.pid ]; then
        echo "Removing stale Docker PID file..."
        rm -f /var/run/docker.pid
    fi

    containerd --log-level debug &
    sleep 10s
    dockerd &
    sleep 10s

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
