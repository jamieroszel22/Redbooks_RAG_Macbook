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
@echo       - ./scripts:/app/scripts:Z >> podman-compose.yml
@echo       - ./data/pdfs:/data/pdfs:Z >> podman-compose.yml
@echo       - ./data/processed_redbooks:/data/processed_redbooks:Z >> podman-compose.yml
@echo       - ./data/openwebui:/data/openwebui:Z >> podman-compose.yml
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
@echo       - ollama_data:/root/.ollama:Z >> podman-compose.yml
@echo     ports: >> podman-compose.yml
@echo       - "11434:11434" >> podman-compose.yml
@echo. >> podman-compose.yml
@echo volumes: >> podman-compose.yml
@echo   ollama_data: >> podman-compose.yml

:: Build and start containers with Podman
echo Building and starting containers with Podman...
podman-compose -f podman-compose.yml up -d --build

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
