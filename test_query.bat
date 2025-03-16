@echo off
echo IBM Redbooks RAG System - Test Query
echo ==================================

REM Check if a query was provided
if "%~1"=="" (
    echo Usage: test_query.bat "Your query here"
    echo Example: test_query.bat "What is IBM Z Cyber Vault?"
    exit /b
)

REM Check if processed files exist
if not exist "C:\Users\jamie\OneDrive\Documents\Redbooks RAG\processed_redbooks\ollama\redbooks_ollama.jsonl" (
    echo Processed data not found.
    echo Please run process_redbooks.bat first.
    exit /b
)

REM Run the RAG system with the provided query
python rag_tester.py --input "C:\Users\jamie\OneDrive\Documents\Redbooks RAG\processed_redbooks\ollama\redbooks_ollama.jsonl" --model granite3.2:8b-instruct-fp16 --query "%~1"
