#!/bin/bash

set -e

FRONT_PORT=${FRONT_PORT:-5173}
BACK_PORT=${BACK_PORT:-8000}

echo "Building frontend image..."

docker build -t das-dashboard .

echo "Frontend image built successfully."

echo "Building backend image..."

docker build -t ui_backend backend/

echo "Backend image built successfully."

echo "Starting backend on port ${BACK_PORT}..."

docker rm -f ui_backend >/dev/null 2>&1 || true

docker run -d \
  --name web-interface-frontend \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v /usr/bin/das-cli:/usr/bin/das-cli:ro \
  -v /opt/web-das:/opt/web-das \
  --network=host \
  ui_backend:latest \
  uvicorn main:dashboard_app --host 0.0.0.0 --port 8000

echo "Backend started successfully."

echo "Starting frontend on port ${FRONT_PORT}..."

docker rm -f das-dashboard >/dev/null 2>&1 || true

docker run -d \
  --name web-interface-backend \
  --network host \
  das-dashboard:latest \
  npm run dev -- --host 0.0.0.0 --port ${FRONT_PORT}

echo "Frontend started successfully."

echo ""
echo "Frontend URL: http://localhost:${FRONT_PORT}"
echo "Backend URL:  http://localhost:${BACK_PORT}"
echo "Backend DOCS URL: http://localhost:${BACK_PORT}/docs"