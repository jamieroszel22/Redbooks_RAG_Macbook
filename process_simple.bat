@echo off
echo IBM Redbooks PDF Processing (Simple Test)
echo =======================================
echo.

set DATA_DIR=C:\Users\jamie\OneDrive\Documents\Redbooks RAG
set SOURCE_DIR=C:\Users\jamie\OneDrive\Documents\Redbooks PDF Content

echo Starting PDF processing...
echo Data Directory: %DATA_DIR%
echo Source Directory: %SOURCE_DIR%
echo.

python redbook-processor.py --data_dir "%DATA_DIR%" --source_dir "%SOURCE_DIR%"

echo.
echo Processing complete.
pause