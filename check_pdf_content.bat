@echo off
echo IBM Redbooks PDF Content Check
echo ===========================
echo.
echo This script will check for PDFs in the Redbooks PDF Content directory.
echo.

set PDF_DIR=C:\Users\jamie\OneDrive\Documents\Redbooks PDF Content

REM Check if directory exists
if not exist "%PDF_DIR%" (
    echo Creating directory %PDF_DIR%...
    mkdir "%PDF_DIR%"
    echo.
    echo No PDFs found (directory was just created).
    echo Please add PDF files to this directory.
    goto :end
)

REM Count and list PDF files
set /a count=0
echo PDF files found in %PDF_DIR%:
echo -------------------------------

for %%F in ("%PDF_DIR%\*.pdf") do (
    echo %%~nxF
    set /a count+=1
)

if %count% equ 0 (
    echo No PDF files found.
    echo Please add PDF files to this directory.
) else (
    echo.
    echo Found %count% PDF files.
    echo.
    echo You can now run process_redbooks.bat to process these files.
)

:end
pause