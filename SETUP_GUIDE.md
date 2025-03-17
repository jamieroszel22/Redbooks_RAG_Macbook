# Complete Setup Guide for IBM Redbooks RAG System

This guide will walk you through setting up the IBM Redbooks RAG system from scratch, including all required components and dependencies.

## Prerequisites

Before starting, ensure you have:
- A computer running Windows, macOS, or Linux
- Python 3.8 or higher installed
- At least 16GB of RAM (32GB recommended)
- Sufficient disk space for PDFs and processed data (at least 20GB free)

## Step 1: Install Ollama

1. Visit [Ollama.ai](https://ollama.ai) and download the installer for your operating system
2. Run the installer and follow the prompts
3. Verify the installation by opening a terminal and running:
   ```bash
   ollama --version
   ```

## Step 2: Pull IBM Granite Models

1. Open a terminal and run the following commands to pull the required models:
   ```bash
   # Pull the base model for embeddings
   ollama pull nomic-embed-text

   # Pull the IBM Granite model for chat
   ollama pull granite3.2:8b-instruct-fp16
   ```

2. Verify the models are installed:
   ```bash
   ollama list
   ```
   You should see both models listed.

## Step 3: Install Open WebUI

1. Visit [Open WebUI GitHub](https://github.com/open-webui/open-webui)
2. Follow the installation instructions for your operating system
3. Start Open WebUI and verify it's running by visiting `http://localhost:3000` in your browser
4. Log in with the default credentials (if prompted)

## Step 4: Set Up the RAG System

1. Clone the repository:
   ```bash
   git clone https://github.com/jamieroszel22/Redbooks_RAG_Macbook.git
   cd Redbooks_RAG_Macbook
   ```

2. Create and activate a Python virtual environment:
   ```bash
   # Create virtual environment
   python -m venv venv

   # Activate it (choose the appropriate command for your OS)
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. Install required Python packages:
   ```bash
   pip install -r requirements.txt
   ```

4. Create the required directories:
   ```bash
   mkdir pdfs
   mkdir processed_redbooks
   mkdir openwebui
   ```

## Step 5: Configure the System

1. Review and adjust the `config.yaml` file if needed:
   ```yaml
   pdf_processing:
     chunk_size: 1000
     overlap: 200

   metadata:
     extract_title: true
     extract_author: true
     extract_date: true
     extract_keywords: true

   paths:
     pdfs_dir: "pdfs"
     processed_dir: "processed_redbooks"
     openwebui_dir: "openwebui"

   collection:
     name: "IBM Z Knowledge Base"
     description: "Processed IBM Redbooks documentation"
   ```

## Step 6: Add IBM Redbooks PDFs

1. Place your IBM Redbooks PDF files in the `pdfs` directory
2. Ensure the PDFs are readable and not corrupted
3. Recommended naming convention: `sg{number}.pdf` (e.g., `sg248952.pdf`)

## Step 7: Process the Documents

1. Run the document processor:
   ```bash
   python document_processor.py
   ```
   This will:
   - Extract metadata from each PDF
   - Split documents into chunks
   - Save processed files in the `processed_redbooks` directory

2. Prepare the files for Open WebUI:
   ```bash
   python prepare_for_openwebui.py
   ```
   This will:
   - Create individual JSON files for each document
   - Generate a main collection file

## Step 8: Import into Open WebUI

1. Open Open WebUI in your browser (`http://localhost:3000`)
2. Navigate to RAG > Collections
3. Click "Import Collection"
4. Select the file `openwebui/IBM_Z_Knowledge_Base.json`
5. Wait for the import to complete

## Step 9: Test the System

1. In Open WebUI:
   - Start a new chat
   - Enable RAG in the chat settings
   - Select the "IBM Z Knowledge Base" collection
   - Try asking a question about IBM Z systems

2. Test the simple query interface:
   ```bash
   python simple_query.py
   ```
   Enter a query when prompted.

## Troubleshooting

### Common Issues

1. **Ollama not running**
   - Ensure Ollama is installed and running
   - Check if the service is active
   - Try restarting Ollama

2. **Open WebUI connection issues**
   - Verify Open WebUI is running
   - Check if port 3000 is available
   - Ensure you can access `http://localhost:3000`

3. **PDF processing errors**
   - Check if PDFs are readable
   - Verify sufficient disk space
   - Check Python environment is activated

4. **Model loading issues**
   - Verify models are downloaded
   - Check available RAM
   - Try pulling models again

### Getting Help

- Check the [GitHub Issues](https://github.com/jamieroszel22/Redbooks_RAG_Macbook/issues)
- Review the [Open WebUI Documentation](https://github.com/open-webui/open-webui/wiki)
- Consult the [Ollama Documentation](https://github.com/ollama/ollama)

## Maintenance

### Adding New Documents

1. Place new PDFs in the `pdfs` directory
2. Run the document processor:
   ```bash
   python document_processor.py
   ```
3. Update Open WebUI collections:
   ```bash
   python prepare_for_openwebui.py
   ```
4. Import the updated collection in Open WebUI

### Updating the System

1. Pull latest changes:
   ```bash
   git pull origin main
   ```
2. Update Python packages:
   ```bash
   pip install -r requirements.txt
   ```
3. Check for model updates:
   ```bash
   ollama pull granite3.2:8b-instruct-fp16
   ```

## Best Practices

1. **Regular Backups**
   - Keep copies of your PDFs
   - Back up the `processed_redbooks` directory
   - Export Open WebUI collections periodically

2. **System Maintenance**
   - Monitor disk space
   - Clean up temporary files
   - Update components regularly

3. **Document Organization**
   - Use consistent naming conventions
   - Keep PDFs in good condition
   - Document any special processing requirements

## Support

For additional support or questions:
- Open an issue on the [GitHub repository](https://github.com/jamieroszel22/Redbooks_RAG_Macbook/issues)
- Check the [Open WebUI community](https://github.com/open-webui/open-webui/discussions)
- Review the [Ollama community](https://github.com/ollama/ollama/discussions)
