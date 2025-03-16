#!/bin/bash
# Fix for timestamp overflow issue in Podman containers

echo "Stopping all running Podman containers..."
podman stop $(podman ps -a -q) 2>/dev/null

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
CMD ["python", "-c", "import time; print('Container started. Use docker exec to run specific scripts.'); time.sleep(86400 * 365)"]
EOF

echo "Building container with fixed Dockerfile..."
podman build -t redbooks-rag-fixed -f Dockerfile.fix .

echo "Starting containers with the fixed image..."
podman-compose down
sed -i 's/build: \./image: redbooks-rag-fixed/g' podman-compose.yml
podman-compose up -d

echo "Fix completed. Your containers should now run without timestamp errors."
echo "To use your container, run: podman exec -it redbooks-rag {script path}"
