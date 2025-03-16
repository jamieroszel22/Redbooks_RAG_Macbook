@echo off
echo IBM Redbooks RAG System - Document Processing
echo ============================================

REM Check if PDFs exist in the pdfs directory
if not exist "pdfs\*.pdf" (
    echo No PDF files found in the pdfs directory.
    echo Please place your IBM Redbooks PDFs in the pdfs directory.
    exit /b
)

REM Process all PDFs in the pdfs directory
echo Processing PDF files in pdfs directory...
python redbook-processor.py --input "pdfs" --output "C:\Users\jamie\OneDrive\Documents\Redbooks RAG\processed_redbooks" --enable-ocr --prepare-ollama

echo.
echo Document processing complete!
echo Processed files are in "C:\Users\jamie\OneDrive\Documents\Redbooks RAG\processed_redbooks"
echo.
echo You can now query the RAG system with:
echo run_simple_query.bat
echo.
