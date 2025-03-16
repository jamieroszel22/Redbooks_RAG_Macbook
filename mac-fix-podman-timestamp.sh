#!/bin/bash
# macOS-specific fix for timestamp overflow issue in Podman containers

echo "MacOS detected - applying special Podman timestamp fixes..."

# Reset podman machine to ensure clean state
echo "Resetting Podman machine..."
podman machine stop || true
podman machine rm -f || true
podman machine init --disk-size 20
podman machine start

echo "Creating Dockerfile with timestamp fix..."
cat > Dockerfile.fix << 'EOF'
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
CMD ["python", "-c", "import time; print('Container started. Use docker exec to run specific scripts.'); time.sleep(86400)"]
EOF

echo "Building container with fixed Dockerfile..."
podman build -t redbooks-rag-fixed -f Dockerfile.fix .

echo "Checking if podman-compose.yml exists and updating it..."
if [ -f podman-compose.yml ]; then
    echo "Updating podman-compose.yml to use fixed image..."
    sed -i '' 's/build: \./image: redbooks-rag-fixed/g' podman-compose.yml
    echo "Starting containers with podman-compose..."
    podman-compose down
    podman-compose up -d
else
    echo "Starting containers manually..."
    podman run -d --name redbooks-ollama -p 11434:11434 -v ollama_data:/root/.ollama:z ollama/ollama:latest
    sleep 5
    podman run -d --name redbooks-rag -p 8000:8000 \
        -v ./scripts:/app/scripts:z \
        -v ./data/pdfs:/data/pdfs:z \
        -v ./data/processed_redbooks:/data/processed_redbooks:z \
        -v ./data/openwebui:/data/openwebui:z \
        -e OLLAMA_BASE_URL=http://redbooks-ollama:11434 \
        --network=host \
        redbooks-rag-fixed
fi

echo "Fix completed. Your containers should now run without timestamp errors."
echo "To use your container, run: podman exec -it redbooks-rag {script path}"
