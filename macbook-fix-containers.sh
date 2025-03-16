#!/bin/bash
# Script to fix the infinity error and restart containers on macOS

echo "Fixing the container issue on macOS..."

# Stop and remove any existing containers
echo "Stopping and removing existing containers..."
podman stop redbooks-rag redbooks-ollama 2>/dev/null || true
podman rm redbooks-rag redbooks-ollama 2>/dev/null || true

# Remove any pods if they exist
PODS=$(podman pod ls -q)
if [ ! -z "$PODS" ]; then
    podman pod rm $PODS
    echo "Removed existing pods."
fi

echo "Checking Podman machine status..."
if ! podman machine list | grep -q "Currently running"; then
    echo "Starting Podman machine..."
    podman machine start
fi

echo "Creating necessary directories..."
mkdir -p data/pdfs
mkdir -p data/processed_redbooks/docs
mkdir -p data/processed_redbooks/chunks
mkdir -p data/processed_redbooks/ollama
mkdir -p data/openwebui

echo "Building containers with fixed Dockerfile..."
podman-compose -f podman-compose.yml up -d --build

echo ""
echo "Verifying container status..."
podman ps

echo ""
echo "If containers are now running, you can proceed with:"
echo "podman exec redbooks-rag sh /app/scripts/process_redbooks.sh"
echo ""
echo "If containers are still not running, check the logs with:"
echo "podman logs redbooks-rag"
