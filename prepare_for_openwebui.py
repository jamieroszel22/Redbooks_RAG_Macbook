import argparse
import json
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("openwebui-prep")

def prepare_for_openwebui(
    input_jsonl: Path,
    output_json: Path,
    collection_name: str = "IBM Redbooks Knowledge Base"
):
    """
    Convert Ollama-style JSONL to Open WebUI knowledge base format.
    
    Args:
        input_jsonl: Path to input JSONL file
        output_json: Path to output JSON file
        collection_name: Name for the collection
    """
    # Read input JSONL
    documents = []
    try:
        with open(input_jsonl, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    documents.append(json.loads(line))
        
        logger.info(f"Loaded {len(documents)} documents from {input_jsonl}")
    except Exception as e:
        logger.error(f"Error reading input file: {e}")
        return False
    
    # Create collection object
    collection = {
        "name": collection_name,
        "description": "IBM Redbooks processed with Docling for RAG",
        "documents": []
    }
    
    # Transform documents to Open WebUI format
    for doc in documents:
        text = doc.get("text", "")
        metadata = doc.get("metadata", {})
        source = metadata.get("source", "unknown")
        
        # Create document in Open WebUI format
        document = {
            "title": f"IBM Redbook: {source}",
            "content": text,
            "metadata": {
                "source": source,
                "processed_date": metadata.get("processed_date", ""),
                "chunk": metadata.get("chunk", 0)
            }
        }
        
        collection["documents"].append(document)
    
    # Write output JSON
    try:
        output_json.parent.mkdir(parents=True, exist_ok=True)
        with open(output_json, "w", encoding="utf-8") as f:
            json.dump(collection, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Created Open WebUI collection at: {output_json}")
        logger.info(f"Collection contains {len(collection['documents'])} documents")
        return True
    except Exception as e:
        logger.error(f"Error writing output file: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Prepare IBM Redbooks for Open WebUI")
    parser.add_argument(
        "--input", "-i", 
        default="C:/Users/jamie/OneDrive/Documents/Redbooks RAG/processed_redbooks/ollama/redbooks_ollama.jsonl",
        help="Path to input JSONL file"
    )
    parser.add_argument(
        "--output", "-o", 
        default="C:/Users/jamie/OneDrive/Documents/Redbooks RAG/openwebui/ibm_redbooks_collection.json",
        help="Path to output JSON file"
    )
    parser.add_argument(
        "--name", "-n", 
        default="IBM Redbooks Knowledge Base",
        help="Name for the collection"
    )
    
    args = parser.parse_args()
    
    success = prepare_for_openwebui(
        input_jsonl=Path(args.input),
        output_json=Path(args.output),
        collection_name=args.name
    )
    
    if success:
        print("\nFile prepared successfully for Open WebUI!")
        print(f"Output JSON file: {args.output}")
        print("\nNext steps:")
        print("1. Log in to Open WebUI at http://192.168.86.19:3000/")
        print("2. Go to Knowledge Management section")
        print("3. Create a new collection and upload the JSON file")
        print("4. Select your model for embeddings")
        print("5. Start a new chat with RAG enabled\n")
    else:
        print("\nFailed to prepare file for Open WebUI.")
        print("Check the logs for details.")

if __name__ == "__main__":
    main()
