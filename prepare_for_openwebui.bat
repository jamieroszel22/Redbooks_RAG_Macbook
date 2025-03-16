@echo off
echo IBM Redbooks RAG - Prepare for Open WebUI
echo =======================================

REM Create output directory if it doesn't exist
mkdir "C:\Users\jamie\OneDrive\Documents\Redbooks RAG\openwebui" 2>nul

REM Check if processed files exist
if not exist "C:\Users\jamie\OneDrive\Documents\Redbooks RAG\processed_redbooks\ollama\redbooks_ollama.jsonl" (
    echo Processed JSONL file not found.
    echo Please run process_redbooks.bat first.
    exit /b
)

REM Convert JSONL to Open WebUI format
python prepare_for_openwebui.py --input "C:\Users\jamie\OneDrive\Documents\Redbooks RAG\processed_redbooks\ollama\redbooks_ollama.jsonl" --output "C:\Users\jamie\OneDrive\Documents\Redbooks RAG\openwebui\ibm_redbooks_collection.json" --name "IBM Z Knowledge Base"

echo.
echo When the conversion is complete, follow these steps:
echo 1. Log in to Open WebUI at http://192.168.86.19:3000/
echo 2. Go to Knowledge Management section
echo 3. Create a new collection and upload the JSON file
echo 4. Select the same model you use for chat (like granite3.2:8b-instruct-fp16) for embeddings
echo 5. Start a new chat with RAG enabled
echo.
