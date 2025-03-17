@echo off
echo IBM Redbooks PDF Content Check
echo ===========================
echo.

set PDF_DIR=C:\Users\jamie\OneDrive\Documents\Redbooks PDF Content

if not exist "%PDF_DIR%" (
    mkdir "%PDF_DIR%"
    echo Directory created: %PDF_DIR%
)

echo Files in directory:
dir "%PDF_DIR%\*.pdf" 

echo.
echo Script complete.
pause