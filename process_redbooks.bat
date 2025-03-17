@echo off
echo IBM Redbooks PDF Processing
echo ===========================
echo.
echo This script will process PDF files from the source directory
echo and the pdfs directory.
echo.

set DATA_DIR=C:\Users\jamie\OneDrive\Documents\Redbooks RAG
set SOURCE_DIR=C:\Users\jamie\OneDrive\Documents\Redbooks PDF Content

REM Check if source directory exists
if not exist "%SOURCE_DIR%" (
    echo Warning: Source directory %SOURCE_DIR% not found.
    echo Creating directory...
    mkdir "%SOURCE_DIR%"
)

REM Check if PDFs exist in either location
set PDF_FOUND=0

dir "%DATA_DIR%\pdfs\*.pdf" /b >nul 2>&1
if %ERRORLEVEL% equ 0 set PDF_FOUND=1

dir "%SOURCE_DIR%\*.pdf" /b >nul 2>&1
if %ERRORLEVEL% equ 0 set PDF_FOUND=1

if %PDF_FOUND% equ 0 (
    echo No PDF files found in either:
    echo - %DATA_DIR%\pdfs
    echo - %SOURCE_DIR%
    echo Please add PDF files first.
    goto :end
)

echo Found PDF files to process.
echo.
echo This may take a while depending on the number and size of PDFs.
echo.
echo Processing...
echo.

python redbook-processor.py --data_dir "%DATA_DIR%" --source_dir "%SOURCE_DIR%"

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
