@echo off
echo IBM Redbooks Simple Query System
echo ===============================
echo.
echo This script will start a simple keyword-based query system.
echo No Ollama or LLM required for this mode.
echo.

set DATA_DIR=C:\Users\jamie\OneDrive\Documents\Redbooks RAG

REM Check if chunks exist
if not exist "%DATA_DIR%\processed_redbooks\chunks" (
    echo No document chunks found in %DATA_DIR%\processed_redbooks\chunks
    echo Please process PDFs first using process_redbooks.bat
    goto :end
)

echo Starting simple query system...
echo.

python simple_query.py --data_dir "%DATA_DIR%"

:end
pause
