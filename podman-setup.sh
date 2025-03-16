#!/bin/bash
# Setup script for Podman on macOS/Linux

# Detect if running on macOS
if [[ "$OSTYPE" == "darwin"* ]]; then
  echo "macOS detected, using macOS-specific setup script..."
  # Check if macbook-podman-reset.sh exists and is executable
  if [ -f "./macbook-podman-reset.sh" ] && [ -x "./macbook-podman-reset.sh" ]; then
    ./macbook-podman-reset.sh
    exit $?
  else
    echo "macbook-podman-reset.sh not found or not executable."
    echo "Making it executable and running it..."
    chmod +x macbook-podman-reset.sh 2>/dev/null
    if [ -x "./macbook-podman-reset.sh" ]; then
      ./macbook-podman-reset.sh
      exit $?
    else
      echo "WARNING: Could not find or execute macbook-podman-reset.sh"
      echo "Continuing with standard setup, but you may encounter issues."
    fi
  fi
fi

echo "Setting up IBM Redbooks RAG System with Podman..."

# Create necessary directories
mkdir -p data/pdfs
mkdir -p data/processed_redbooks/docs
mkdir -p data/processed_redbooks/chunks
mkdir -p data/processed_redbooks/ollama
mkdir -p data/openwebui

# Create Podman-compatible compose file
echo "Creating Podman-compatible compose file..."
cat > podman-compose.yml << 'EOL'
version: '3'

services:
  redbooks-rag:
    build: .
    container_name: redbooks-rag
    volumes:
      - ./scripts:/app/scripts:Z
      - ./data/pdfs:/data/pdfs:Z
      - ./data/processed_redbooks:/data/processed_redbooks:Z
      - ./data/openwebui:/data/openwebui:Z
    environment:
      - OLLAMA_BASE_URL=http://redbooks-ollama:11434
    depends_on:
      - ollama
    ports:
      - "8000:8000"
    tty: true
    stdin_open: true

  ollama:
    image: ollama/ollama:latest
    container_name: redbooks-ollama
    volumes:
      - ollama_data:/root/.ollama:Z
    ports:
      - "11434:11434"

volumes:
  ollama_data:
EOL

# Ensure Podman machine is running if on macOS
if [[ "$OSTYPE" == "darwin"* ]]; then
  echo "Checking Podman machine status..."
  if ! podman machine list | grep -q "Currently running"; then
    echo "Starting Podman machine..."
    podman machine start
  fi
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
