#!/bin/bash

if docker info > /dev/null 2>&1; then
    echo "Docker is already running."
else
    echo "Starting dockerd..."
    
    if [ -f /var/run/docker.pid ]; then
        echo "Removing stale Docker PID file..."
        rm -f /var/run/docker.pid
    fi

    containerd --log-level debug > /dev/null 2>&1 &
    sleep 10s
    dockerd > /dev/null 2>&1 &
    sleep 10s

    if ! docker info > /dev/null 2>&1; then
        echo "ERROR: Docker is not running!"
        cat /var/log/dockerd.log
        exit 1
    fi
fi

exec make "$@"
