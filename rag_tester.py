import argparse
import json
import logging
import os
import time
from pathlib import Path
import requests

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Ollama API settings
OLLAMA_BASE_URL = "http://localhost:11434/api"
DEFAULT_MODEL = "granite3.2:8b-instruct-fp16"

def check_ollama_available():
    """Check if Ollama server is running."""
    try:
        response = requests.get(f"{OLLAMA_BASE_URL}/tags")
        if response.status_code == 200:
            models = response.json().get("models", [])
            print(f"Ollama is running. Available models:")
            for model in models:
                print(f"- {model['name']}")
            return True
        return False
    except requests.RequestException:
        return False

def check_directory_structure(base_dir):
    """Check that the expected directory structure exists."""
    paths = {
        "pdfs": Path(base_dir) / "pdfs",
        "processed": Path(base_dir) / "processed_redbooks",
        "docs": Path(base_dir) / "processed_redbooks" / "docs",
        "chunks": Path(base_dir) / "processed_redbooks" / "chunks",
        "ollama": Path(base_dir) / "processed_redbooks" / "ollama",
        "openwebui": Path(base_dir) / "openwebui"
    }
    
    missing = []
    for name, path in paths.items():
        if not path.exists():
            missing.append(name)
    
    if missing:
        print(f"WARNING: The following directories are missing: {', '.join(missing)}")
        return False
    
    print("All expected directories exist.")
    return True

def test_gpu_detection():
    """Test the GPU detection script."""
    print("Testing GPU detection...")
    
    try:
        import subprocess
        import sys
        
        result = subprocess.run([sys.executable, "check_gpu.py"], 
                               stdout=subprocess.PIPE, 
                               stderr=subprocess.PIPE,
                               text=True)
        
        print(result.stdout)
        
        if result.returncode == 0:
            print("GPU detection test passed. GPU is available.")
            return True
        else:
            print("GPU detection test passed. No GPU detected.")
            return False
    except Exception as e:
        print(f"GPU detection test failed: {str(e)}")
        return False

def test_document_processing(base_dir, sample_pdf=None):
    """Test document processing with a small PDF."""
    if not sample_pdf:
        # Check if there's a PDF to test with
        pdf_dir = Path(base_dir) / "pdfs"
        pdf_files = list(pdf_dir.glob("*.pdf"))
        
        if not pdf_files:
            print("No PDF files found for testing document processing.")
            return False
        
        # Use the smallest PDF for testing
        sample_pdf = min(pdf_files, key=lambda p: p.stat().st_size)
    
    print(f"Testing document processing with {sample_pdf}...")
    
    try:
        import subprocess
        import sys
        
        cmd = [
            sys.executable, 
            "redbook-processor.py", 
            "--data_dir", 
            base_dir,
            "--specific_pdf",
            str(sample_pdf)
        ]
        
        process = subprocess.Popen(cmd, 
                                  stdout=subprocess.PIPE, 
                                  stderr=subprocess.PIPE,
                                  text=True,
                                  bufsize=1)
        
        # Print output in real-time
        for line in process.stdout:
            print(line.strip())
        
        process.wait()
        
        if process.returncode == 0:
            print("Document processing test passed.")
            return True
        else:
            error = process.stderr.read()
            print(f"Document processing test failed: {error}")
            return False
    except Exception as e:
        print(f"Document processing test failed: {str(e)}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Test the IBM Redbooks RAG system")
    parser.add_argument("--data_dir", type=str, default="C:\\Users\\jamie\\OneDrive\\Documents\\Redbooks RAG", 
                        help="Base directory for data storage")
    parser.add_argument("--test_pdf", type=str, help="Specific PDF to test processing with")
    args = parser.parse_args()
    
    print("Running IBM Redbooks RAG System Tests")
    print("=" * 50)
    
    # Test GPU detection
    gpu_available = test_gpu_detection()
    print("-" * 50)
    
    # Check directory structure
    dirs_ok = check_directory_structure(args.data_dir)
    print("-" * 50)
    
    # Check Ollama
    ollama_ok = check_ollama_available()
    if not ollama_ok:
        print("WARNING: Ollama is not available. Make sure it's running for RAG functionality.")
    print("-" * 50)
    
    # Test document processing if a test PDF is provided
    if args.test_pdf:
        test_pdf_path = Path(args.test_pdf)
        if test_pdf_path.exists():
            processing_ok = test_document_processing(args.data_dir, test_pdf_path)
        else:
            print(f"Test PDF not found: {args.test_pdf}")
            processing_ok = False
    else:
        # Skip document processing test if no test PDF
        processing_ok = None
        print("Skipping document processing test. Use --test_pdf to run this test.")
    
    print("-" * 50)
    print("Test Results Summary:")
    print(f"GPU Available: {'Yes' if gpu_available else 'No'}")
    print(f"Directory Structure: {'OK' if dirs_ok else 'Issues Found'}")
    print(f"Ollama Available: {'Yes' if ollama_ok else 'No'}")
    
    if processing_ok is not None:
        print(f"Document Processing: {'Success' if processing_ok else 'Failed'}")
    else:
        print("Document Processing: Not Tested")

if __name__ == "__main__":
    main()
