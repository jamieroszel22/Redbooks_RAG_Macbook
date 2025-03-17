@echo off
echo IBM Redbooks RAG System Test
echo =========================
echo.
echo This script will test the components of your RAG system.
echo.

set DATA_DIR=C:\Users\jamie\OneDrive\Documents\Redbooks RAG

REM Run the tester script
python rag_tester.py --data_dir "%DATA_DIR%"

echo.
echo Test complete.
echo.

pause
