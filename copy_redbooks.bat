@echo off
echo Copying IBM Redbooks PDFs...
echo ==========================

REM Create the destination directory if it doesn't exist
mkdir "C:\Users\jamie\OneDrive\Documents\Redbooks RAG\pdfs" 2>nul

REM Copy IBM Redbooks PDFs from Downloads
echo Copying IBM Redbooks from Downloads...
copy "C:\Users\jamie\Downloads\sg248*.pdf" "C:\Users\jamie\OneDrive\Documents\Redbooks RAG\pdfs\" 2>nul

echo.
echo IBM Redbooks PDFs have been copied to:
echo "C:\Users\jamie\OneDrive\Documents\Redbooks RAG\pdfs\"
echo.
echo You can now run process_redbooks.bat to process these files.
echo.
