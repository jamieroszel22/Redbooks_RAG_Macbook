#!/bin/bash
# Setup script for Linux/Mac

echo "Setting up IBM Redbooks RAG System..."

# Create necessary data directories
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
