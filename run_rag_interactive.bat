@echo off
echo IBM Redbooks RAG Interactive System
echo =================================
echo.
echo This script will start the Ollama-based RAG system.
echo Make sure Ollama is running on http://localhost:11434
echo.

set DATA_DIR=C:\Users\jamie\OneDrive\Documents\Redbooks RAG
set MODEL=granite3.2:8b-instruct-fp16

REM Check if chunks exist
if not exist "%DATA_DIR%\processed_redbooks\chunks" (
    echo No document chunks found in %DATA_DIR%\processed_redbooks\chunks
    echo Please process PDFs first using process_redbooks.bat
    goto :end
)

echo Checking Ollama connection...
curl -s http://localhost:11434/api/tags >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo ERROR: Ollama not available at http://localhost:11434
    echo Please make sure Ollama is running.
    goto :end
)

echo Ollama is running. Starting RAG system...
echo Using model: %MODEL%
echo.
echo Note: First-time use will generate embeddings, which may take a while.
echo.

python ollama-rag-integration.py --data_dir "%DATA_DIR%" --model "%MODEL%"

:end
pause
