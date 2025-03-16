@echo off
echo Setting up IBM Redbooks RAG System with Podman...

:: Create necessary data directories
mkdir data\pdfs 2>nul
mkdir data\processed_redbooks\docs 2>nul
mkdir data\processed_redbooks\chunks 2>nul
mkdir data\processed_redbooks\ollama 2>nul
mkdir data\openwebui 2>nul

:: Create Podman-compatible compose file
echo Creating Podman-compatible compose file...

@echo version: '3' > podman-compose.yml
@echo. >> podman-compose.yml
@echo services: >> podman-compose.yml
@echo   redbooks-rag: >> podman-compose.yml
@echo     build: . >> podman-compose.yml
@echo     container_name: redbooks-rag >> podman-compose.yml
@echo     volumes: >> podman-compose.yml
@echo       - ./scripts:/app/scripts:z >> podman-compose.yml
@echo       - ./data/pdfs:/data/pdfs:z >> podman-compose.yml
@echo       - ./data/processed_redbooks:/data/processed_redbooks:z >> podman-compose.yml
@echo       - ./data/openwebui:/data/openwebui:z >> podman-compose.yml
@echo     environment: >> podman-compose.yml
@echo       - OLLAMA_BASE_URL=http://redbooks-ollama:11434 >> podman-compose.yml
@echo     depends_on: >> podman-compose.yml
@echo       - ollama >> podman-compose.yml
@echo     ports: >> podman-compose.yml
@echo       - "8000:8000" >> podman-compose.yml
@echo     tty: true >> podman-compose.yml
@echo     stdin_open: true >> podman-compose.yml
@echo. >> podman-compose.yml
@echo   ollama: >> podman-compose.yml
@echo     image: ollama/ollama:latest >> podman-compose.yml
@echo     container_name: redbooks-ollama >> podman-compose.yml
@echo     volumes: >> podman-compose.yml
@echo       - ollama_data:/root/.ollama:z >> podman-compose.yml
@echo     ports: >> podman-compose.yml
@echo       - "11434:11434" >> podman-compose.yml
@echo. >> podman-compose.yml
@echo volumes: >> podman-compose.yml
@echo   ollama_data: >> podman-compose.yml

:: Build and start containers with Podman
echo Building and starting containers with Podman...

:: Use our fixed Dockerfile to prevent timestamp errors
echo FROM python:3.10-slim > Dockerfile.fix
echo. >> Dockerfile.fix
echo WORKDIR /app >> Dockerfile.fix
echo. >> Dockerfile.fix
echo # Install system dependencies >> Dockerfile.fix
echo RUN apt-get update ^&^& apt-get install -y \ >> Dockerfile.fix
echo     build-essential \ >> Dockerfile.fix
echo     git \ >> Dockerfile.fix
echo     poppler-utils \ >> Dockerfile.fix
echo     tesseract-ocr \ >> Dockerfile.fix
echo     ^&^& apt-get clean \ >> Dockerfile.fix
echo     ^&^& rm -rf /var/lib/apt/lists/* >> Dockerfile.fix
echo. >> Dockerfile.fix
echo # Copy requirements first to leverage Docker caching >> Dockerfile.fix
echo COPY requirements.txt . >> Dockerfile.fix
echo RUN pip install --no-cache-dir -r requirements.txt >> Dockerfile.fix
echo. >> Dockerfile.fix
echo # Copy project files >> Dockerfile.fix
echo COPY redbook-processor.py . >> Dockerfile.fix
echo COPY ollama-rag-integration.py . >> Dockerfile.fix
echo COPY simple_query.py . >> Dockerfile.fix
echo COPY prepare_for_openwebui.py . >> Dockerfile.fix
echo COPY check_gpu.py . >> Dockerfile.fix
echo COPY rag_tester.py . >> Dockerfile.fix
echo. >> Dockerfile.fix
echo # Create required directories >> Dockerfile.fix
echo RUN mkdir -p /data/pdfs /data/processed_redbooks/docs /data/processed_redbooks/chunks /data/processed_redbooks/ollama /data/openwebui >> Dockerfile.fix
echo. >> Dockerfile.fix
echo # Set environment variables >> Dockerfile.fix
echo ENV PYTHONUNBUFFERED=1 >> Dockerfile.fix
echo # Fix for timestamp overflow issue in containerized environments >> Dockerfile.fix
echo ENV PYTHONMAXINT=9223372036854775807 >> Dockerfile.fix
echo. >> Dockerfile.fix
echo # Volume for persistent data >> Dockerfile.fix
echo VOLUME ["/data"] >> Dockerfile.fix
echo. >> Dockerfile.fix
echo # Command to run when container starts - using a large but finite sleep time >> Dockerfile.fix
echo CMD ["python", "-c", "import time; print('Container started. Use docker exec to run specific scripts.'); time.sleep(86400 * 365)"] >> Dockerfile.fix

echo Building fixed container image...
podman build -t redbooks-rag-fixed -f Dockerfile.fix .

echo Updating compose file to use fixed image...
powershell -Command "(Get-Content podman-compose.yml) -replace 'build: \.', 'image: redbooks-rag-fixed' | Set-Content podman-compose.yml"

podman-compose -f podman-compose.yml up -d

echo.
echo Setup complete!
echo.
echo To process Redbooks, place PDF files in the data\pdfs directory,
echo then run: podman exec redbooks-rag sh /app/scripts/process_redbooks.sh
echo.
echo To use the RAG system interactively, run:
echo podman exec -it redbooks-rag sh /app/scripts/run_rag_interactive.sh
echo.
echo For Open WebUI integration, run:
echo podman exec redbooks-rag sh /app/scripts/prepare_for_openwebui.sh
echo.
