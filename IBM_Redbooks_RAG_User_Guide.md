# IBM Redbooks RAG System - User Guide

This guide explains how to use the containerized IBM Redbooks RAG system to query IBM technical documentation through natural language.

## Getting Started

### Prerequisites

- Docker Desktop installed (Windows, Mac, or Linux)
- For optimal performance: NVIDIA GPU with CUDA support
- At least 8GB of RAM, 16GB recommended
- 10GB+ of free disk space

### Installation

1. Download and extract the IBM Redbooks RAG system ZIP file
2. Open a command prompt or terminal in the extracted directory
3. Run the setup script:
   - On Windows: `setup.bat`
   - On Linux/Mac: `chmod +x setup.sh && ./setup.sh`

The setup will create the necessary directories and start the Docker containers.

## Using the System

### Processing IBM Redbooks

1. Place IBM Redbook PDF files in the `data/pdfs` directory
2. Process the PDFs by running:
   ```
   docker exec redbooks-rag sh /app/scripts/process_redbooks.sh
   ```
3. Wait for processing to complete (may take several minutes per document)

### Querying the Knowledge Base

#### Interactive Command Line

1. Start the interactive session:
   ```
   docker exec -it redbooks-rag sh /app/scripts/run_rag_interactive.sh
   ```
2. Enter your questions at the prompt
3. Type `exit` to quit the session

#### Using Open WebUI

1. Prepare data for Open WebUI:
   ```
   docker exec redbooks-rag sh /app/scripts/prepare_for_openwebui.sh
   ```
2. Follow these steps to set up Open WebUI:
   - Install Open WebUI following their documentation
   - Create a new collection named "IBM Z Knowledge Base"
   - Upload the JSON files from the `data/openwebui` directory
   - Enable RAG in your chat settings

## Example Queries

Try asking questions like:
- "What is the purpose of the IBM Z Processor?"
- "How do I configure high availability on IBM Z systems?"
- "Explain the difference between LPAR and z/VM"
- "What security features are available in z/OS?"

## Troubleshooting

### Common Issues

**The container won't start**
- Check if Docker is running
- Ensure you have enough system resources
- Try running `docker-compose down` followed by `docker-compose up -d`

**Processing errors with PDFs**
- Ensure PDFs are not password-protected
- Try with a different PDF to isolate the issue

**Model gives inaccurate answers**
- Try rephrasing your question
- Ensure relevant Redbooks are processed
- Consider using a larger language model

### Getting Support

If you encounter issues not covered here, please check the project's GitHub repository for updates or contact the maintainer.

## Advanced Configuration

See the README.md file for advanced configuration options, including:
- Changing the language model
- Customizing data paths
- Optimizing for different hardware
