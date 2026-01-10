#!/bin/bash

LOG_PATH="/var/lib/docker/containers/"
THRESHOLD=70

# Check if disk usage is above threshold
USAGE=$(df --output=pcent / | grep -v "Use" | tr -d '%')

if [ "$USAGE" -lt "$THRESHOLD" ]; then
    exit 0
fi
else
    # Find and clean container built up log files
    sudo find $LOG_PATH -type f -name "*.log" -exec truncate -s 0 {} \;

    # Run docker commands to clean up unused volumes, images and build cache
    docker system prune --volumes -f -a

    docker builder prune -f -a

    docker volume prune -f -a
fi