# IBM Redbooks RAG System - Local Setup Guide

This guide explains how to use the IBM Redbooks RAG system on your local PC without containerization.

## System Requirements

- Python 3.9 or higher
- Docling library (for document processing)
- PyTorch (for enhanced document processing)
- Ollama (for local LLM access)
- 16GB RAM recommended (8GB minimum)
- GPU recommended but not required

## Directory Structure

- `C:\Users\jamie\OneDrive\Desktop\ibm_redbooks_rag\` - Main project directory with scripts
- `C:\Users\jamie\OneDrive\Desktop\ibm_redbooks_rag\pdfs\` - Place your IBM Redbook PDFs here
- `C:\Users\jamie\OneDrive\Documents\Redbooks RAG\processed_redbooks\` - Output directory with:
  - `docs/` - Processed documents (Markdown, HTML, JSON)
  - `chunks/` - Text chunks for retrieval
  - `ollama/` - JSONL files formatted for Ollama RAG

## Getting Started

1. Run `check_local_setup.bat` to verify your environment is set up correctly
2. Place IBM Redbook PDFs in the `pdfs` directory
3. Run `process_redbooks.bat` to process the documents
4. Start Ollama server (if not already running)
5. Run `run_rag_interactive.bat` to query the knowledge base

## Available Scripts

- `check_local_setup.bat` - Verifies your local environment
- `process_redbooks.bat` - Processes PDFs with Docling
- `run_rag_interactive.bat` - Runs embedding-based RAG with Ollama
- `run_simple_query.bat` - Runs keyword-based RAG without embeddings
- `prepare_for_openwebui.bat` - Converts to Open WebUI format

## Advanced Usage

### Processing Options

The document processor supports several options:

```
python redbook-processor.py --input "pdfs" --output "path/to/output" [OPTIONS]

Options:
  --enable-ocr         Enable OCR for scanned content
  --chunk-size N       Set custom chunk size (default: 1000)
  --debug              Enable debug visualizations
  --skip-chunking      Skip the chunking step
```

### Using Different Models

You can use different Ollama models by modifying the model parameter:

```
python ollama-rag-integration.py --model different-model-name --interactive
```

## Troubleshooting

If you encounter issues:

1. Check if Ollama is running (`curl http://localhost:11434/api/version`)
2. Ensure you have enough disk space for processed documents
3. Try running with `--enable-ocr` if documents contain scanned text
4. Check the console output for specific error messages

## Next Steps

- For a web interface, try integrating with Open WebUI
- Experiment with different chunk sizes for optimal retrieval
- Try different Ollama models to compare performance
