#!/bin/bash
set -e

USER_ID=${UID:-1000}
GROUP_ID=${GID:-1000}

groupadd -g "$GROUP_ID" dasgroup || true
useradd -m -u "$USER_ID" -g "$GROUP_ID" -s /bin/bash dasuser || true

chown -R "$USER_ID:$GROUP_ID" /app

exec gosu dasuser make local-build
