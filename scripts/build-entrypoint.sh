#!/bin/bash
set -e

USER_ID=${UID:-1000}
GROUP_ID=${GID:-1000}

DOCKER_GID=$(stat -c '%g' /var/run/docker.sock)

groupadd -g "$DOCKER_GID" docker || true

groupadd -g "$GROUP_ID" dasgroup || true
useradd -m -u "$USER_ID" -g "$GROUP_ID" -G docker -s /bin/bash dasuser || true

chown -R "$USER_ID:$GROUP_ID" /app

exec gosu dasuser make build-local
