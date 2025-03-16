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

# Volume for persistent data
VOLUME ["/data"]

# Command to run when container starts
CMD ["python", "-c", "import time; print('Container started. Use docker exec to run specific scripts.'); time.sleep(infinity)"]
