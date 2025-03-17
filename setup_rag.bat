@echo off
echo Setting up IBM Redbooks RAG System...
echo.

REM Create necessary directories
mkdir "C:\Users\jamie\OneDrive\Documents\Redbooks RAG" 2>nul
mkdir "C:\Users\jamie\OneDrive\Documents\Redbooks RAG\pdfs" 2>nul
mkdir "C:\Users\jamie\OneDrive\Documents\Redbooks RAG\processed_redbooks" 2>nul
mkdir "C:\Users\jamie\OneDrive\Documents\Redbooks RAG\processed_redbooks\docs" 2>nul
mkdir "C:\Users\jamie\OneDrive\Documents\Redbooks RAG\processed_redbooks\chunks" 2>nul
mkdir "C:\Users\jamie\OneDrive\Documents\Redbooks RAG\processed_redbooks\ollama" 2>nul
mkdir "C:\Users\jamie\OneDrive\Documents\Redbooks RAG\openwebui" 2>nul

echo Directory structure created.
echo.

REM Check for Python
python --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo ERROR: Python not found. Please install Python 3.8 or higher.
    goto :error
)

REM Check for required Python packages
echo Installing required Python packages...
pip install docling torch colorama tqdm requests numpy >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo WARNING: Some packages may not have installed correctly.
) else (
    echo Required packages installed successfully.
)
echo.

REM Test GPU availability
echo Testing GPU availability...
python check_gpu.py
echo.

REM Instructions
echo Setup complete!
echo.
echo Next steps:
echo 1. Place your IBM Redbooks PDFs in: C:\Users\jamie\OneDrive\Documents\Redbooks RAG\pdfs
echo 2. Run process_redbooks.bat to process the PDFs
echo 3. Use run_simple_query.bat or run_rag_interactive.bat to query your documents
echo 4. Use prepare_for_openwebui.bat to prepare data for Open WebUI
echo.
echo Enjoy your IBM Redbooks RAG System!
goto :end

:error
echo Setup failed. Please fix the errors and try again.

:end
pause
