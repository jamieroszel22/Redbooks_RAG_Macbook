@echo off
echo Setting up IBM Redbooks RAG System...

:: Create necessary data directories
mkdir data\pdfs 2>nul
mkdir data\processed_redbooks\docs 2>nul
mkdir data\processed_redbooks\chunks 2>nul
mkdir data\processed_redbooks\ollama 2>nul
mkdir data\openwebui 2>nul

:: Build and start Docker containers
echo Building and starting Docker containers...
docker-compose up -d --build

echo.
echo Setup complete!
echo.
echo To process Redbooks, place PDF files in the data\pdfs directory,
echo then run: docker exec redbooks-rag sh /app/scripts/process_redbooks.sh
echo.
echo To use the RAG system interactively, run:
echo docker exec -it redbooks-rag sh /app/scripts/run_rag_interactive.sh
echo.
echo For Open WebUI integration, run:
echo docker exec redbooks-rag sh /app/scripts/prepare_for_openwebui.sh
echo.
