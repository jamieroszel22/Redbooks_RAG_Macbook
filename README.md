# IBM Redbooks RAG System

[![Docker Build Test](https://github.com/jamieroszel22/docling_rag/actions/workflows/docker-build.yml/badge.svg)](https://github.com/jamieroszel22/docling_rag/actions/workflows/docker-build.yml)

A containerized Retrieval-Augmented Generation (RAG) system for IBM Redbooks technical documentation that leverages Docling for PDF processing and understanding.

## Prerequisites

- Docker and Docker Compose
- NVIDIA GPU with drivers installed (for optimal performance)
- NVIDIA Container Toolkit (for GPU support)

## Quick Start

1. Clone this repository:
   ```bash
   git clone https://github.com/jamieroszel22/docling_rag.git
   cd docling_rag
   ```

2. Place your IBM Redbooks PDFs in the `data/pdfs` directory (will be created automatically)

3. Run the setup script to initialize the environment:
   ```bash
   # On Windows
   setup.bat
   
   # On Linux/Mac
   chmod +x setup.sh && ./setup.sh
   ```

4. Process your Redbooks:
   ```bash
   docker exec redbooks-rag sh /app/scripts/process_redbooks.sh
   ```

5. Run the interactive RAG system:
   ```bash
   docker exec -it redbooks-rag sh /app/scripts/run_rag_interactive.sh
   ```

6. Prepare data for Open WebUI (optional):
   ```bash
   docker exec redbooks-rag sh /app/scripts/prepare_for_openwebui.sh
   ```

## Configuration

Edit the `.env` file to configure:
- Custom paths for your data
- Ollama model to use

## Project Structure

```
├── Dockerfile            # Container definition
├── docker-compose.yml    # Multi-container setup
├── requirements.txt      # Python dependencies
├── scripts/              # Helper scripts
│   ├── process_redbooks.sh
│   ├── run_rag_interactive.sh
│   └── prepare_for_openwebui.sh
├── data/                 # Data directory (created on first run)
│   ├── pdfs/             # Place your Redbook PDFs here
│   ├── processed_redbooks/
│   │   ├── docs/         # Processed documents
│   │   ├── chunks/       # Text chunks for retrieval
│   │   └── ollama/       # JSONL files for Ollama
│   └── openwebui/        # Files for Open WebUI integration
```

## Open WebUI Integration

After running the `prepare_for_openwebui.sh` script, the files in the `data/openwebui` directory can be uploaded to your Open WebUI instance as a collection named "IBM Z Knowledge Base".

1. Access your Open WebUI instance
2. Create a new collection
3. Upload the JSON files from the `data/openwebui` directory
4. Enable RAG when chatting with the model

## LLM Support

This container comes with Ollama, which can run various models. The default configuration uses:
- granite3.2:8b-instruct-fp16

To use a different model, edit the `.env` file and change the `OLLAMA_MODEL` variable.

## Development

To contribute to this project:

1. Fork the repository on GitHub
2. Create a new branch for your feature
3. Commit your changes
4. Push to your branch
5. Create a new Pull Request

## CI/CD

This project uses GitHub Actions for continuous integration. Each push to the main branch will trigger a Docker build test to ensure the container builds successfully.

## Troubleshooting

- If you encounter GPU-related issues, check that the NVIDIA Container Toolkit is properly installed.
- For memory issues, you may need to adjust the model size in the `.env` file.
- Check container logs with: `docker logs redbooks-rag` or `docker logs redbooks-ollama`

## About

This project uses [Docling](https://github.com/DS4SD/docling) for advanced PDF understanding and document processing.
