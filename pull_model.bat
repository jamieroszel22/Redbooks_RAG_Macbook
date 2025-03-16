@echo off
echo IBM Redbooks RAG System - Pull Ollama Models
echo =========================================

set MODEL=granite3.2:8b-instruct-fp16

if not "%~1"=="" (
    set MODEL=%~1
)

echo Pulling model: %MODEL%...
ollama pull %MODEL%

echo.
echo Model pulled successfully!
echo.
