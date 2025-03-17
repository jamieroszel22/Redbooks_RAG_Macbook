# IBM Redbooks RAG System

This system provides a complete Retrieval-Augmented Generation (RAG) solution for IBM Redbooks technical documentation. It processes PDF documents into queryable knowledge bases that can be accessed through natural language, enabling technical users to quickly find specific information in IBM's extensive documentation.

## Features

- Process PDF documents using Docling for advanced document understanding
- Support for GPU acceleration with NVIDIA GPUs
- Simple keyword-based search without requiring an LLM
- Advanced RAG using Ollama for embedding-based retrieval and generation
- Integration with Open WebUI for a user-friendly interface
- Batch files for easy operation

## System Requirements

- Windows with Python 3.8 or higher
- For GPU acceleration: NVIDIA GPU with CUDA support (e.g., RTX 4070 Ti Super)
- [Ollama](https://ollama.ai/) for LLM functionality
- [Open WebUI](https://github.com/open-webui/open-webui) (optional, for web interface)

## Directory Structure

- Main Project Directory: `C:\Users\jamie\OneDrive\Desktop\ibm_redbooks_rag\`
  - Contains all Python scripts and batch files

- Data Directory: `C:\Users\jamie\OneDrive\Documents\Redbooks RAG\`
  - `/pdfs/` - Storage for IBM Redbook PDF files
  - `/processed_redbooks/` - Contains processed documents and chunks
    - `/processed_redbooks/docs/` - Markdown, HTML, JSON of processed documents
    - `/processed_redbooks/chunks/` - Text chunks for retrieval
    - `/processed_redbooks/ollama/` - JSONL files formatted for Ollama
  - `/openwebui/` - Contains JSON files for Open WebUI integration

## Scripts

### Python Scripts
- `redbook-processor.py` - Main document processing script
- `ollama-rag-integration.py` - Embedding-based RAG with Ollama
- `simple_query.py` - Keyword-based RAG without embeddings
- `prepare_for_openwebui.py` - Converts to Open WebUI format
- `check_gpu.py` - Check for GPU presence and capabilities
- `rag_tester.py` - Test the RAG system

### Batch Files
- `setup_rag.bat` - Initial setup script
- `process_redbooks.bat` - Processes PDFs with Docling
- `run_simple_query.bat` - Runs keyword-based RAG
- `run_rag_interactive.bat` - Runs embedding-based RAG
- `prepare_for_openwebui.bat` - Prepares data for Open WebUI
- `copy_redbooks.bat` - Helper to copy PDFs to the right location
- `test_query.bat` - Test the RAG system

## Getting Started

1. Run `setup_rag.bat` to set up directories and install dependencies
2. Place IBM Redbooks PDFs in the `pdfs` directory (or use `copy_redbooks.bat` to help)
3. Run `process_redbooks.bat` to process the PDFs
4. Choose an interaction method:
   - For simple search without LLM: Run `run_simple_query.bat`
   - For Ollama-based RAG: Run `run_rag_interactive.bat`
   - For Open WebUI: Run `prepare_for_openwebui.bat` and follow instructions

## External Integration

### Ollama
- Expected to run locally at http://localhost:11434
- Default model: `granite3.2:8b-instruct-fp16` (can be changed in `run_rag_interactive.bat`)

### Open WebUI
- Collection name: "IBM Z Knowledge Base" (can be changed in `prepare_for_openwebui.bat`)
- Import generated JSON file from the `openwebui` directory

## Troubleshooting

- Run `test_query.bat` to test system components
- Check that Ollama is running for LLM-based features
- Ensure PDFs are properly formatted and readable

## Customization

- Edit `ollama-rag-integration.py` to modify the system prompt or embedding settings
- Change the collection name in `prepare_for_openwebui.bat` for different document sets
- Adjust chunk size in `redbook-processor.py` for different document types

## Further Development

This project can be extended to:
- Support additional document formats (Docling supports many formats beyond PDF)
- Add multi-collection support for different document libraries
- Implement hybrid retrieval strategies (combining keyword and embedding search)
- Add support for other LLM providers beyond Ollama
