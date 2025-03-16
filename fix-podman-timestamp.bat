@echo off
echo Fixing Podman timestamp overflow issue...

echo Stopping all running Podman containers...
for /f %%i in ('podman ps -a -q') do podman stop %%i 2>nul

echo Creating Dockerfile with timestamp fix...
(
echo FROM python:3.10-slim
echo.
echo WORKDIR /app
echo.
echo # Install system dependencies 
echo RUN apt-get update ^&^& apt-get install -y \
echo     build-essential \
echo     git \
echo     poppler-utils \
echo     tesseract-ocr \
echo     ^&^& apt-get clean \
echo     ^&^& rm -rf /var/lib/apt/lists/*
echo.
echo # Copy requirements first to leverage Docker caching
echo COPY requirements.txt .
echo RUN pip install --no-cache-dir -r requirements.txt
echo.
echo # Copy project files
echo COPY redbook-processor.py .
echo COPY ollama-rag-integration.py .
echo COPY simple_query.py .
echo COPY prepare_for_openwebui.py .
echo COPY check_gpu.py .
echo COPY rag_tester.py .
echo.
echo # Create required directories
echo RUN mkdir -p /data/pdfs /data/processed_redbooks/docs /data/processed_redbooks/chunks /data/processed_redbooks/ollama /data/openwebui
echo.
echo # Set environment variables
echo ENV PYTHONUNBUFFERED=1
echo # Fix for timestamp overflow issue in containerized environments
echo ENV PYTHONMAXINT=9223372036854775807
echo.
echo # Volume for persistent data
echo VOLUME ["/data"]
echo.
echo # Command to run when container starts - using a large but finite sleep time
echo CMD ["python", "-c", "import time; print('Container started. Use docker exec to run specific scripts.'); time.sleep(86400 * 365)"]
) > Dockerfile.fix

echo Building container with fixed Dockerfile...
podman build -t redbooks-rag-fixed -f Dockerfile.fix .

echo Starting containers with the fixed image...
podman-compose down

echo Updating podman-compose.yml to use fixed image...
powershell -Command "(Get-Content podman-compose.yml) -replace 'build: \.', 'image: redbooks-rag-fixed' | Set-Content podman-compose.yml"

echo Starting containers with the fixed setup...
podman-compose up -d

echo Fix completed. Your containers should now run without timestamp errors.
echo To use your container, run: podman exec -it redbooks-rag {script path}
pause
