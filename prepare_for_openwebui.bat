@echo off
echo IBM Redbooks Open WebUI Integration
echo =================================
echo.
echo This script will prepare your data for Open WebUI.
echo.

set DATA_DIR=C:\Users\jamie\OneDrive\Documents\Redbooks RAG
set COLLECTION=IBM Z Knowledge Base

REM Check if chunks exist
if not exist "%DATA_DIR%\processed_redbooks\chunks" (
    echo No document chunks found in %DATA_DIR%\processed_redbooks\chunks
    echo Please process PDFs first using process_redbooks.bat
    goto :end
)

echo Preparing data for Open WebUI...
echo Collection name: %COLLECTION%
echo.

python prepare_for_openwebui.py --data_dir "%DATA_DIR%" --collection "%COLLECTION%"

echo.
echo The Open WebUI collection file is ready.
echo See the import instructions file for next steps.
echo.

:end
pause
