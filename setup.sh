#!/bin/bash
# Setup script for Linux/Mac

# Detect if running on macOS
if [[ "$OSTYPE" == "darwin"* ]]; then
  echo "macOS detected!"
  
  # Check if Docker Desktop is installed
  if command -v docker &> /dev/null; then
    # Offer choice between Docker and Podman
    echo ""
    echo "You're running on macOS, which setup would you prefer?"
    echo "1) Docker (more reliable on macOS)"
    echo "2) Podman (recommended for IBM environments)"
    read -p "Enter choice [1-2] (default: 1): " choice
    
    case "$choice" in
      2)
        echo "Using Podman on macOS..."
        chmod +x podman-setup.sh
        ./podman-setup.sh
        exit $?
        ;;
      *)
        echo "Using Docker on macOS..."
        chmod +x macbook-docker-setup.sh
        ./macbook-docker-setup.sh
        exit $?
        ;;
    esac
  fi
fi

echo "Setting up IBM Redbooks RAG System..."

# Create necessary directories
mkdir -p data/pdfs
mkdir -p data/processed_redbooks/docs
mkdir -p data/processed_redbooks/chunks
mkdir -p data/processed_redbooks/ollama
mkdir -p data/openwebui

# Build and start Docker containers
echo "Building and starting Docker containers..."
docker-compose up -d --build

echo ""
echo "Setup complete!"
echo ""
echo "To process Redbooks, place PDF files in the data/pdfs directory,"
echo "then run: docker exec redbooks-rag sh /app/scripts/process_redbooks.sh"
echo ""
echo "To use the RAG system interactively, run:"
echo "docker exec -it redbooks-rag sh /app/scripts/run_rag_interactive.sh"
echo ""
echo "For Open WebUI integration, run:"
echo "docker exec redbooks-rag sh /app/scripts/prepare_for_openwebui.sh"
echo ""
