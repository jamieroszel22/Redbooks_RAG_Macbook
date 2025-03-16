#!/bin/bash
# Setup script for Podman on Linux/Mac

echo "Setting up IBM Redbooks RAG System with Podman..."

# Create necessary directories
mkdir -p data/pdfs
mkdir -p data/processed_redbooks/docs
mkdir -p data/processed_redbooks/chunks
mkdir -p data/processed_redbooks/ollama
mkdir -p data/openwebui

# Create Podman-compatible compose file
if [ ! -f "podman-compose.yml" ]; then
  echo "Creating Podman-compatible compose file..."
  cp docker-compose.yml podman-compose.yml
fi

# Build and start containers with Podman
echo "Building and starting containers with Podman..."
podman-compose -f podman-compose.yml up -d --build

echo ""
echo "Setup complete!"
echo ""
echo "To process Redbooks, place PDF files in the data/pdfs directory,"
echo "then run: podman exec redbooks-rag sh /app/scripts/process_redbooks.sh"
echo ""
echo "To use the RAG system interactively, run:"
echo "podman exec -it redbooks-rag sh /app/scripts/run_rag_interactive.sh"
echo ""
echo "For Open WebUI integration, run:"
echo "podman exec redbooks-rag sh /app/scripts/prepare_for_openwebui.sh"
echo ""
