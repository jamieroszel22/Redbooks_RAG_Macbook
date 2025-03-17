@echo off
echo IBM Redbooks Copy Utility
echo =======================
echo.
echo This script helps you copy PDF files to the appropriate directory.
echo.

set TARGET_DIR=C:\Users\jamie\OneDrive\Documents\Redbooks RAG\pdfs

REM Create directory if it doesn't exist
if not exist "%TARGET_DIR%" mkdir "%TARGET_DIR%"

echo Please select PDF files to copy to %TARGET_DIR%
echo.

REM Use PowerShell to create a file selection dialog
powershell -Command "Add-Type -AssemblyName System.Windows.Forms; $f = New-Object System.Windows.Forms.OpenFileDialog -Property @{Multiselect = $true; Filter = 'PDF Files (*.pdf)|*.pdf'}; $null = $f.ShowDialog(); $f.FileNames" > "%TEMP%\selected_files.txt"

REM Process selected files
set /p FILES=<"%TEMP%\selected_files.txt"

REM Check if files were selected
if "%FILES%"=="" (
    echo No files selected.
    goto :end
)

REM Copy each file
for %%F in (%FILES%) do (
    echo Copying %%F to %TARGET_DIR%...
    copy "%%F" "%TARGET_DIR%"
)

echo.
echo Files copied successfully.
echo.
echo You now have the following PDF files in your directory:
dir "%TARGET_DIR%\*.pdf" /b

:end
del "%TEMP%\selected_files.txt" >nul 2>&1
pause
