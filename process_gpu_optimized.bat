@echo off
echo IBM Redbooks PDF Processing (GPU Optimized)
echo =======================================
echo.

set DATA_DIR=C:\Users\jamie\OneDrive\Documents\Redbooks RAG
set SOURCE_DIR=C:\Users\jamie\OneDrive\Documents\Redbooks PDF Content

echo Starting GPU-optimized PDF processing...
echo Data Directory: %DATA_DIR%
echo Source Directory: %SOURCE_DIR%
echo.

REM Set environment variables for GPU optimization
set DOCLING_USE_GPU=1
set DOCLING_DEVICE=cuda
set CUDA_VISIBLE_DEVICES=0

echo Testing GPU first...
python test_gpu_usage.py

echo.
echo Starting PDF processing with GPU optimization...
echo.

python redbook-processor.py --data_dir "%DATA_DIR%" --source_dir "%SOURCE_DIR%"

echo.
echo Processing complete.
pause
