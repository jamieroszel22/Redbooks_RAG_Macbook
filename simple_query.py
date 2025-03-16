import argparse
import json
import logging
import re
from pathlib import Path
import requests

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("simple-rag-query")

def search_chunks(jsonl_file, query, top_k=5):
    """Simple keyword-based search for chunks without embeddings."""
    
    # Load chunks from JSONL file
    chunks = []
    with open(jsonl_file, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            chunk = json.loads(line)
            chunks.append(chunk)
    
    logger.info(f"Loaded {len(chunks)} chunks from {jsonl_file}")
    
    # Create search terms from query (split into words, remove punctuation, lowercase)
    search_terms = re.sub(r'[^\w\s]', '', query.lower()).split()
    
    # Score each chunk based on term frequency
    chunk_scores = []
    for chunk in chunks:
        text = chunk["text"].lower()
        score = 0
        for term in search_terms:
            score += text.count(term)
        if score > 0:  # Only include chunks with matches
            chunk_scores.append((chunk, score))
    
    # Sort by score (highest first)
    chunk_scores.sort(key=lambda x: x[1], reverse=True)
    
    # Return top_k results
    top_results = chunk_scores[:top_k]
    return top_results

def query_with_context(query, context_chunks, model="granite3.2:8b-instruct-fp16", host="localhost", port=11434):
    """Query model with context chunks."""
    
    ollama_url = f"http://{host}:{port}"
    
    # Format context for the prompt
    formatted_context = "\n\n".join([f"Context document {i+1}:\n{chunk['text']}" for i, (chunk, _) in enumerate(context_chunks)])
    
    # Build the prompt with context
    prompt = f"""You are a helpful assistant with access to IBM Redbooks information. 
Use the following context to answer the question, and if the information is not in the context, say so.

{formatted_context}

Question: {query}

Answer:"""
    
    # Send request to Ollama
    try:
        response = requests.post(
            f"{ollama_url}/api/generate",
            json={
                "model": model,
                "prompt": prompt,
                "temperature": 0.7,
                "max_tokens": 500,
                "stream": False
            }
        )
        
        if response.status_code != 200:
            return f"Error: {response.text}"
            
        return response.json().get("response", "No response received")
    except Exception as e:
        return f"Error connecting to Ollama: {e}"

def main():
    parser = argparse.ArgumentParser(description="Simple IBM Redbooks RAG Query (no embeddings)")
    parser.add_argument(
        "--input", "-i", 
        default="./processed_redbooks/ollama/redbooks_ollama.jsonl",
        help="Path to JSONL file with processed chunks"
    )
    parser.add_argument(
        "--model", "-m", 
        default="granite3.2:8b-instruct-fp16",
        help="Ollama model to use"
    )
    parser.add_argument(
        "--port", "-p", 
        type=int,
        default=11434,
        help="Ollama API port"
    )
    parser.add_argument(
        "--host", 
        default="localhost",
        help="Ollama API host"
    )
    parser.add_argument(
        "--interactive", 
        action="store_true",
        help="Run in interactive query mode"
    )
    parser.add_argument(
        "--query", "-q",
        help="Single query to run (non-interactive mode)"
    )
    parser.add_argument(
        "--top-k", "-k",
        type=int,
        default=5,
        help="Number of top results to use"
    )
    
    args = parser.parse_args()
    
    # Check if model exists
    ollama_url = f"http://{args.host}:{args.port}"
    try:
        response = requests.get(f"{ollama_url}/api/tags")
        if response.status_code != 200:
            logger.error(f"Error connecting to Ollama: {response.text}")
            return
            
        # Check if model is in the list
        models = response.json().get("models", [])
        model_names = [model.get("name") for model in models]
        
        if args.model not in model_names:
            logger.warning(f"Model '{args.model}' not found in available models: {', '.join(model_names)}")
            logger.warning(f"You may need to pull it with: ollama pull {args.model}")
    except Exception as e:
        logger.error(f"Error checking Ollama models: {e}")
    
    # Execute query or run interactive mode
    if args.query:
        # Single query mode
        logger.info(f"Executing query: {args.query}")
        
        # Get relevant chunks using simple keyword search
        results = search_chunks(args.input, args.query, args.top_k)
        
        logger.info(f"Found {len(results)} relevant chunks")
        for i, (chunk, score) in enumerate(results):
            logger.info(f"Result {i+1} (score: {score}):")
            source = chunk["metadata"].get("source", "unknown") if "metadata" in chunk else "unknown"
            logger.info(f"Source: {source}")
            # Print first 150 chars as preview
            logger.info(f"Preview: {chunk['text'][:150]}...")
        
        # Generate response with context
        response = query_with_context(args.query, results, args.model, args.host, args.port)
        
        print("\n" + "="*50)
        print("ANSWER:")
        print("="*50)
        print(response)
        print("="*50)
        
    elif args.interactive:
        # Interactive mode
        print("\nIBM Redbooks RAG with Ollama (Simple Search)")
        print("Type 'quit' or 'exit' to end the session")
        
        while True:
            query = input("\nEnter your query: ")
            if query.lower() in ("quit", "exit"):
                break
                
            # Get relevant chunks using simple keyword search
            results = search_chunks(args.input, query, args.top_k)
            
            if not results:
                print("No relevant information found in documents. Try a different query.")
                continue
                
            # Generate response with context
            response = query_with_context(query, results, args.model, args.host, args.port)
            
            print("\n" + "="*50)
            print("ANSWER:")
            print("="*50)
            print(response)
            print("="*50)
    else:
        logger.info("Use --query or --interactive to run queries.")

if __name__ == "__main__":
    main()
