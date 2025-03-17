# IBM Redbooks RAG System

This system provides a complete Retrieval-Augmented Generation (RAG) solution for IBM Redbooks technical documentation. It processes PDF documents into queryable knowledge bases that can be accessed through natural language, enabling technical users to quickly find specific information in IBM's extensive documentation.

## Features

- Centralized configuration system with `config.yaml`
- Advanced metadata extraction from PDFs
- Individual JSON files per document for better organization
- Incremental processing support
- Simple keyword-based search without requiring an LLM
- Advanced RAG using Ollama for embedding-based retrieval and generation
- Integration with Open WebUI for a user-friendly interface
- Cross-platform support (Windows, macOS, Linux)

## System Requirements

- Python 3.8 or higher
- PyMuPDF for PDF processing
- PyYAML for configuration management
- [Ollama](https://ollama.ai/) for LLM functionality
- [Open WebUI](https://github.com/open-webui/open-webui) (optional, for web interface)

## Directory Structure

```
.
├── config.yaml                 # Central configuration file
├── pdfs/                      # Source PDF documents
├── processed_redbooks/        # Processed documents
│   ├── {document_id}/        # Per-document directories
│   │   ├── metadata.json     # Document metadata
│   │   └── chunks/           # Document chunks
├── openwebui/                 # Open WebUI integration files
│   ├── {document_id}.json    # Individual document collections
│   └── IBM_Z_Knowledge_Base.json  # Main collection file
└── venv/                      # Python virtual environment
```

## Core Components

### Configuration System (`config.yaml`)
- PDF processing parameters
- Metadata extraction settings
- File paths and naming conventions
- Collection settings
- Quality check parameters

### Python Scripts
- `config_loader.py` - Configuration management
- `metadata_extractor.py` - PDF metadata extraction
- `document_processor.py` - Main document processing
- `prepare_for_openwebui.py` - Open WebUI integration
- `simple_query.py` - Keyword-based search

## Getting Started

1. Clone the repository:
   ```bash
   git clone https://github.com/jamieroszel22/Redbooks_RAG_Macbook.git
   cd Redbooks_RAG_Macbook
   ```

2. Set up the Python environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Place IBM Redbooks PDFs in the `pdfs` directory

4. Process the documents:
   ```bash
   python document_processor.py
   ```

5. Prepare for Open WebUI:
   ```bash
   python prepare_for_openwebui.py
   ```

6. Import into Open WebUI:
   - Navigate to RAG > Collections in Open WebUI
   - Import the main collection file from `openwebui/IBM_Z_Knowledge_Base.json`
   - Individual document collections are also available in the `openwebui` directory

## Configuration

The `config.yaml` file controls all aspects of the system:

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

## Adding New Documents

1. Place new PDFs in the `pdfs` directory
2. Run the document processor:
   ```bash
   python document_processor.py
   ```
3. Update Open WebUI collections:
   ```bash
   python prepare_for_openwebui.py
   ```

## Querying the Knowledge Base

### Via Open WebUI
1. Start a new chat
2. Enable RAG
3. Select the "IBM Z Knowledge Base" collection
4. Ask questions about IBM Z systems

### Via Simple Query
```bash
python simple_query.py
```

## Customization

- Modify `config.yaml` to adjust processing parameters
- Edit metadata extraction rules in `metadata_extractor.py`
- Customize collection organization in `prepare_for_openwebui.py`

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for improvements.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
