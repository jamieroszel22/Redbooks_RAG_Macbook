import argparse
import json
import logging
import os
import time
import uuid
from pathlib import Path
from typing import List, Dict, Any

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def load_chunks(chunks_dir: Path) -> List[Dict[str, Any]]:
    """Load all chunks from the chunks directory."""
    chunks = []
    chunk_files = list(chunks_dir.glob("*/*chunk_*.txt"))
    
    # Sort files for consistent loading
    chunk_files.sort()
    
    for chunk_file in chunk_files:
        doc_name = chunk_file.parent.name
        with open(chunk_file, 'r', encoding='utf-8') as f:
            content = f.read()
            chunks.append({
                "document": doc_name,
                "id": chunk_file.stem,
                "content": content,
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
            "chunks": []
        }
        
        # Add all chunks for this document
        for chunk in doc_chunks:
            chunk_data = {
                "id": str(uuid.uuid4()),
                "document_id": doc_id,
                "content": chunk["content"],
                "metadata": {
                    "source": chunk["file_path"],
                    "chunk_id": chunk["id"]
                }
            }
            document_data["chunks"].append(chunk_data)
        
        collection_data["documents"].append(document_data)
    
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
4. Select the file: `{collection_file.name}`
5. Wait for the import to complete
6. Verify your collection "{collection_name}" appears in the list
7. Enable RAG for your chats by selecting this collection
""")
    
    logger.info(f"Created import instructions: {instructions_file}")

def main():
    parser = argparse.ArgumentParser(description="Prepare data for Open WebUI integration")
    parser.add_argument("--data_dir", type=str, default="C:\\Users\\jamie\\OneDrive\\Documents\\Redbooks RAG", 
                        help="Base directory for data storage")
    parser.add_argument("--collection", type=str, default="IBM Z Knowledge Base", 
                        help="Name for the Open WebUI collection")
    args = parser.parse_args()
    
    chunks_dir = Path(args.data_dir) / "processed_redbooks" / "chunks"
    output_dir = Path(args.data_dir) / "openwebui"
    
    if not chunks_dir.exists():
        logger.error(f"Chunks directory not found: {chunks_dir}")
        print(f"Error: Chunks directory not found. Please process PDFs first using redbook-processor.py")
        return
    
    # Create output directory if it doesn't exist
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Load chunks
    chunks = load_chunks(chunks_dir)
    
    # Prepare for Open WebUI
    prepare_for_openwebui(chunks, output_dir, args.collection)
    
    print(f"Successfully prepared data for Open WebUI. Files saved to {output_dir}")
    print(f"Follow the instructions in {output_dir / 'import_instructions.md'} to import the collection.")

if __name__ == "__main__":
    main()
