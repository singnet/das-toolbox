#!/bin/bash
set -e

source ./gh-login.sh

USERID=$(id -u "$USER")
GROUPID=$(id -g "$USER")

cleanup() {
   RUNNER_TOKEN=$(get_github_runner_token "$REPO_URL" "$GH_TOKEN")

    echo "Removing the GitHub Actions runner..."
    sudo -u "$USER" ./config.sh remove --token "$RUNNER_TOKEN" || true
}

trap cleanup SIGINT SIGTERM EXIT

echo "Configuring permissions for the cache folder at /home/$USER/.cache..."
echo "Current user: $USER, User ID: $USERID, Group ID: $GROUPID"

chown "$USERID:$GROUPID" "/home/$USER/.cache" -R

echo "Starting the dockerd..."
dockerd > /var/log/dockerd.log 2>&1 &
sleep 1m

if ! docker info > /dev/null 2>&1; then
    echo "ERROR: Docker is not running!"
    cat /var/log/dockerd.log
    exit 1
fi


echo "Setting permissions for Docker socket..."
chmod 777 /var/run/docker.sock

sudo -u "$USER" ./gh-runner.sh "$REPO_URL" "$GH_TOKEN" &
RUNNER_PID=$!

wait $RUNNER_PID
