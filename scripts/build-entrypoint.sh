#!/bin/bash
set -e

USER_ID=${UID:-1000}
GROUP_ID=${GID:-1000}

export USER="dasuser"

groupadd -g "$GROUP_ID" dasgroup || true
useradd -m -u "$USER_ID" -g "$GROUP_ID" -G docker -s /bin/bash ${USER} || true

chown -R "$USER_ID:$GROUP_ID" /app

git config --global http.version HTTP/1.1
git config --global http.postBuffer 157286400
git clone --depth 1 --branch master https://github.com/singnet/das.git /tmp/das || true
cd /tmp/das && tree && make build-all

exec gosu ${USER} make build-local
