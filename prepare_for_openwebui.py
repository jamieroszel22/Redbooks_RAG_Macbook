import argparse
import json
import logging
import os
import time
import uuid
from pathlib import Path
from typing import List, Dict, Any

from config_loader import ConfigLoader

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def load_chunks(processed_dir: Path) -> List[Dict[str, Any]]:
    """Load all chunks from the processed documents directory."""
    chunks = []
    # Look for chunk files in all document directories
    chunk_files = list(processed_dir.rglob("chunks/chunk_*.json"))

    # Sort files for consistent loading
    chunk_files.sort()

    for chunk_file in chunk_files:
        with open(chunk_file, 'r', encoding='utf-8') as f:
            chunk_data = json.load(f)
            chunks.append({
                "document": chunk_file.parent.parent.name,
                "id": chunk_file.stem,
                "content": chunk_data["content"],
                "metadata": chunk_data["metadata"],
                "file_path": str(chunk_file)
            })

    logger.info(f"Loaded {len(chunks)} chunks from {len(set([c['document'] for c in chunks]))} documents")
    return chunks

def prepare_for_openwebui(chunks: List[Dict[str, Any]], output_dir: Path, collection_name: str = "IBM Z Knowledge Base") -> None:
    """Convert chunks to Open WebUI format."""
    # Create directory if it doesn't exist
    output_dir.mkdir(parents=True, exist_ok=True)

    # Group chunks by document
    docs = {}
    for chunk in chunks:
        doc_name = chunk["document"]
        if doc_name not in docs:
            docs[doc_name] = []
        docs[doc_name].append(chunk)

    # Create collection metadata
    collection_data = {
        "name": collection_name,
        "id": str(uuid.uuid4()),
        "document_count": len(docs),
        "chunk_count": len(chunks),
        "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "documents": []
    }

    # Process each document
    for doc_name, doc_chunks in docs.items():
        # Create document metadata
        doc_id = str(uuid.uuid4())
        document_data = {
            "id": doc_id,
            "name": doc_name,
            "metadata": doc_chunks[0]["metadata"],  # Use metadata from first chunk
            "chunks": []
        }

        # Add all chunks for this document
        for chunk in doc_chunks:
            chunk_data = {
                "id": str(uuid.uuid4()),
                "document_id": doc_id,
                "content": chunk["content"],
                "metadata": chunk["metadata"]
            }
            document_data["chunks"].append(chunk_data)

        # Save individual document file
        doc_file = output_dir / f"{doc_name}.json"
        with open(doc_file, 'w', encoding='utf-8') as f:
            json.dump(document_data, f, indent=2)
        logger.info(f"Created document file: {doc_file}")

        # Add document reference to collection
        collection_data["documents"].append({
            "id": doc_id,
            "name": doc_name,
            "file": doc_file.name,
            "metadata": document_data["metadata"]
        })

    # Save collection file
    collection_file = output_dir / f"{collection_name.replace(' ', '_')}.json"
    with open(collection_file, 'w', encoding='utf-8') as f:
        json.dump(collection_data, f, indent=2)

    logger.info(f"Created Open WebUI collection: {collection_file}")
    logger.info(f"Collection contains {len(collection_data['documents'])} documents with {collection_data['chunk_count']} chunks")

    # Create instruction file for importing
    instructions_file = output_dir / "import_instructions.md"
    with open(instructions_file, 'w', encoding='utf-8') as f:
        f.write(f"""# Instructions for importing to Open WebUI

1. Open your Open WebUI instance
2. Go to RAG > Collections
3. Click "Import Collection"
4. Select the main collection file: `{collection_file.name}`
5. Wait for the import to complete
6. Verify your collection "{collection_name}" appears in the list
7. Enable RAG for your chats by selecting this collection

Note: The collection contains {len(collection_data['documents'])} separate documents:
{chr(10).join(f"- {doc['name']} ({doc['metadata'].get('title', 'No title')})" for doc in collection_data['documents'])}
""")

    logger.info(f"Created import instructions: {instructions_file}")

def main():
    parser = argparse.ArgumentParser(description="Prepare data for Open WebUI integration")
    parser.add_argument("--config", type=str, default="config.yaml",
                        help="Path to configuration file")
    args = parser.parse_args()

    # Load configuration
    config_loader = ConfigLoader(args.config)
    config = config_loader.config

    processed_dir = config_loader.get_path('processed_dir')
    output_dir = config_loader.get_path('output_dir')

    if not processed_dir.exists():
        logger.error(f"Processed directory not found: {processed_dir}")
        print(f"Error: Processed directory not found. Please process PDFs first using document_processor.py")
        return

    # Create output directory if it doesn't exist
    output_dir.mkdir(parents=True, exist_ok=True)

    # Load chunks
    chunks = load_chunks(processed_dir)

    # Prepare for Open WebUI
    prepare_for_openwebui(chunks, output_dir, config['collection']['name'])

    print(f"Successfully prepared data for Open WebUI. Files saved to {output_dir}")
    print(f"Follow the instructions in {output_dir / 'import_instructions.md'} to import the collection.")

if __name__ == "__main__":
    main()
