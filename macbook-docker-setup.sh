#!/bin/bash
# Setup script for Docker on macOS

echo "Setting up IBM Redbooks RAG System with Docker..."

echo "Stopping and removing existing Docker containers..."
# Stop and remove containers if they exist
docker stop redbooks-rag redbooks-ollama 2>/dev/null || true
docker rm redbooks-rag redbooks-ollama 2>/dev/null || true

echo "Creating necessary directories..."
mkdir -p data/pdfs
mkdir -p data/processed_redbooks/docs
mkdir -p data/processed_redbooks/chunks
mkdir -p data/processed_redbooks/ollama
mkdir -p data/openwebui

echo "Creating macOS-compatible compose file..."
cat > docker-compose.yml << 'EOL'
version: '3'

services:
  redbooks-rag:
    build: .
    container_name: redbooks-rag
    volumes:
      - ./scripts:/app/scripts
      - ./data/pdfs:/data/pdfs
      - ./data/processed_redbooks:/data/processed_redbooks
      - ./data/openwebui:/data/openwebui
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
      - ollama_data:/root/.ollama
    ports:
      - "11434:11434"

volumes:
  ollama_data:
EOL

echo "Building and starting containers with Docker..."
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
