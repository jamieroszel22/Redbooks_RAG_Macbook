@echo off
echo Setting up IBM Redbooks RAG System...
echo ===================================

REM Create directories
mkdir "C:\Users\jamie\OneDrive\Documents\Redbooks RAG" 2>nul
mkdir "C:\Users\jamie\OneDrive\Documents\Redbooks RAG\pdfs" 2>nul
mkdir "C:\Users\jamie\OneDrive\Documents\Redbooks RAG\processed_redbooks" 2>nul

REM Copy necessary scripts
copy "*.py" "C:\Users\jamie\OneDrive\Documents\Redbooks RAG\" 2>nul
copy "*.bat" "C:\Users\jamie\OneDrive\Documents\Redbooks RAG\" 2>nul

echo.
echo Installing required Python packages...
pip install docling torch requests numpy scipy

echo.
echo Checking GPU availability...
python check_gpu.py

echo.
echo Setup complete! You can now:
echo 1. Place your IBM Redbooks PDFs in "C:\Users\jamie\OneDrive\Documents\Redbooks RAG\pdfs\"
echo 2. Navigate to "C:\Users\jamie\OneDrive\Documents\Redbooks RAG"
echo 3. Run "process_redbooks.bat" to process your PDFs
echo 4. Run "run_simple_query.bat" to query your processed documents
echo.
