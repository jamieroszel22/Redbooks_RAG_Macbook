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
      - ./scripts:/app/scripts:z
      - ./data/pdfs:/data/pdfs:z
      - ./data/processed_redbooks:/data/processed_redbooks:z
      - ./data/openwebui:/data/openwebui:z
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
      - ollama_data:/root/.ollama:z
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

# Create a fixed Dockerfile to prevent timestamp errors
echo "Creating fixed Dockerfile to prevent timestamp errors..."
cat > Dockerfile.fix << 'EOL'
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies 
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    poppler-utils \
    tesseract-ocr \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY redbook-processor.py .
COPY ollama-rag-integration.py .
COPY simple_query.py .
COPY prepare_for_openwebui.py .
COPY check_gpu.py .
COPY rag_tester.py .

# Create required directories
RUN mkdir -p /data/pdfs /data/processed_redbooks/docs /data/processed_redbooks/chunks /data/processed_redbooks/ollama /data/openwebui

# Set environment variables
ENV PYTHONUNBUFFERED=1
# Fix for timestamp overflow issue in containerized environments
ENV PYTHONMAXINT=9223372036854775807

# Volume for persistent data
VOLUME ["/data"]

# Command to run when container starts - using a large but finite sleep time
CMD ["python", "-c", "import time; print('Container started. Use docker exec to run specific scripts.'); time.sleep(86400 * 365)"]
EOL

echo "Building fixed container image..."
podman build -t redbooks-rag-fixed -f Dockerfile.fix .

echo "Updating compose file to use fixed image..."
sed -i 's/build: \./image: redbooks-rag-fixed/g' podman-compose.yml

podman-compose -f podman-compose.yml up -d

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
