@echo off
echo Setting up IBM Redbooks RAG System with Podman...

:: Create necessary data directories
mkdir data\pdfs 2>nul
mkdir data\processed_redbooks\docs 2>nul
mkdir data\processed_redbooks\chunks 2>nul
mkdir data\processed_redbooks\ollama 2>nul
mkdir data\openwebui 2>nul

:: Create Podman-compatible compose file if it doesn't exist
if not exist podman-compose.yml (
    echo Creating Podman-compatible compose file...
    copy docker-compose.yml podman-compose.yml
)

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
