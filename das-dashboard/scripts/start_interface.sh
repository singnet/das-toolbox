#!/bin/bash

set -e

PACKAGE_VERSION=${PACKAGE_VERSION:-1.0.7}

FRONT_PORT=${FRONT_PORT:-5173}
BACK_PORT=${BACK_PORT:-8000}

echo "Building das-toolbox package version ${PACKAGE_VERSION}..."

make build PACKAGE_VERSION=${PACKAGE_VERSION}

echo "Copying package to backend context..."

cp ./dist/das-toolbox_${PACKAGE_VERSION}_amd64.deb \
   ./das-dashboard/backend/

echo "Building frontend image..."

docker build -t das-dashboard ./das-dashboard

echo "Frontend image built successfully."

echo "Building backend image..."

docker build -t ui_backend ./das-dashboard/backend

echo "Backend image built successfully."

echo "Starting backend on port ${BACK_PORT}..."

docker rm -f ui_backend >/dev/null 2>&1 || true

docker run -d \
  --name ui_backend-das-dashboard \
  -v /var/run/docker.sock:/var/run/docker.sock:ro \
  --network host \
  ui_backend:latest \
  uvicorn main:dashboard_app --host 0.0.0.0 --port ${BACK_PORT}

echo "Backend started successfully."

echo "Starting frontend on port ${FRONT_PORT}..."

docker rm -f das-dashboard >/dev/null 2>&1 || true

docker run -d \
  --name ui-frontend-das-dashboard \
  --network host \
  das-dashboard:latest \
  npm run dev -- --host 0.0.0.0 --port ${FRONT_PORT}

echo "Frontend started successfully."

echo ""
echo "Frontend URL: http://localhost:${FRONT_PORT}"
echo "Backend URL:  http://localhost:${BACK_PORT}"
echo "Backend DOCS URL: http://localhost:${BACK_PORT}/docs"