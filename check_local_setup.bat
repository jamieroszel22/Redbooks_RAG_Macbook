@echo off
echo Checking IBM Redbooks RAG local environment setup...
echo ================================================

REM Verify Python installation
echo Checking Python installation...
python --version
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Python is not installed or not in PATH.
    echo Please install Python 3.9 or higher.
    exit /b
)

REM Check required packages
echo.
echo Checking required packages...
python -c "import docling" 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo WARNING: Docling package not found.
    echo Installing docling...
    python -m pip install docling
)

python -c "import torch" 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo WARNING: PyTorch package not found.
    echo Installing PyTorch...
    python -m pip install torch
)

REM Check directory structure
echo.
echo Checking directory structure...
if not exist "pdfs" (
    echo Creating pdfs directory...
    mkdir pdfs
)

REM Check Ollama installation
echo.
echo Checking Ollama server...
curl -s http://localhost:11434/api/version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo WARNING: Ollama server not running on localhost:11434
    echo Please start Ollama before running RAG queries.
) else (
    echo Ollama server is running.
)

echo.
echo IBM Redbooks RAG local environment check complete!
echo.
echo To use the system:
echo 1. Place IBM Redbook PDFs in the pdfs directory
echo 2. Run process_redbooks.bat to process them
echo 3. Run run_rag_interactive.bat to query them
echo.
pause
