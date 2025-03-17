@echo off
echo IBM Redbooks PDF Processing
echo ===========================
echo.
echo This script will process all PDF files in the pdfs directory.
echo.

set DATA_DIR=C:\Users\jamie\OneDrive\Documents\Redbooks RAG

REM Check if PDFs exist
dir "%DATA_DIR%\pdfs\*.pdf" /b >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo No PDF files found in %DATA_DIR%\pdfs
    echo Please add PDF files first.
    goto :end
)

echo Found PDF files to process.
echo.
echo This may take a while depending on the number and size of PDFs.
echo.
echo Processing...
echo.

python redbook-processor.py --data_dir "%DATA_DIR%"

echo.
echo PDF processing complete.
echo.
echo Your processed documents are available in:
echo %DATA_DIR%\processed_redbooks\docs
echo.
echo Your document chunks are available in:
echo %DATA_DIR%\processed_redbooks\chunks
echo.

:end
pause
