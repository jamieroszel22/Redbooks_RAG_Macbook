import argparse
import json
import logging
import time
from pathlib import Path

import requests

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("rag-tester")

def test_ollama_rag(
    query: str,
    jsonl_file: Path,
    model: str = "llama3",
    host: str = "localhost",
    port: int = 11434,
    top_k: int = 3,
    temperature: float = 0.7
):
    """
    Test Ollama RAG with a given query.
    
    Args:
        query: Query to test
        jsonl_file: Path to JSONL file with chunks
        model: Ollama model to use
        host: Ollama host
        port: Ollama port
        top_k: Number of top results to use for context
        temperature: Model temperature
    """
    ollama_url = f"http://{host}:{port}"
    
    logger.info(f"Testing query: {query}")
    logger.info(f"Using model: {model} on {ollama_url}")
    
    # Load chunks
    chunks = []
    with open(jsonl_file, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            chunk = json.loads(line)
            chunks.append(chunk)
    
    logger.info(f"Loaded {len(chunks)} chunks from {jsonl_file}")
    
    # Test if model exists first
    logger.info("Testing model availability...")
    try:
        test_response = requests.post(
            f"{ollama_url}/api/embeddings",
            json={"model": model, "prompt": "Test"}
        )
        
        if test_response.status_code != 200:
            error_msg = test_response.text
            if "model not found" in error_msg.lower():
                logger.error(f"Model '{model}' not found. Please pull it with 'ollama pull {model}'")
                logger.error(f"Alternatively, specify a different model with --model")
                logger.error(f"Available models can be listed with 'ollama list'")
                return
            else:
                logger.error(f"Error connecting to Ollama: {error_msg}")
                return
    except Exception as e:
        logger.error(f"Error connecting to Ollama service: {e}")
        logger.error("Make sure Ollama is running with 'ollama serve'")
        return
    
    # Generate embeddings for the query
    logger.info("Generating query embedding...")
    start_time = time.time()
    
    try:
        embedding_response = requests.post(
            f"{ollama_url}/api/embeddings",
            json={"model": model, "prompt": query}
        )
        
        if embedding_response.status_code != 200:
            logger.error(f"Error generating embedding: {embedding_response.text}")
            return
        
        query_embedding = embedding_response.json().get("embedding")
    except Exception as e:
        logger.error(f"Exception while generating query embedding: {e}")
        return
    
    # Generate embeddings for chunks (in batches)
    logger.info("Generating embeddings for chunks (this may take a while)...")
    
    chunk_embeddings = []
    batch_size = 10  # Process in small batches to avoid long requests
    
    for i in range(0, len(chunks), batch_size):
        batch_chunks = chunks[i:i+batch_size]
        logger.info(f"Processing batch {i//batch_size + 1}/{(len(chunks) + batch_size - 1)//batch_size}")
        
        for chunk in batch_chunks:
            chunk_response = requests.post(
                f"{ollama_url}/api/embeddings",
                json={"model": model, "prompt": chunk["text"]}
            )
            
            if chunk_response.status_code != 200:
                logger.error(f"Error generating embedding: {chunk_response.text}")
                continue
                
            chunk_embedding = chunk_response.json().get("embedding")
            if chunk_embedding:
                chunk_embeddings.append((chunk, chunk_embedding))
    
    embedding_time = time.time() - start_time
    logger.info(f"Generated {len(chunk_embeddings)} embeddings in {embedding_time:.2f} seconds")
    
    # Calculate cosine similarity and sort
    from scipy.spatial.distance import cosine
    
    similarities = []
    for chunk, embedding in chunk_embeddings:
        similarity = 1 - cosine(query_embedding, embedding)
        similarities.append((chunk, similarity))
    
    # Sort by similarity (descending)
    similarities.sort(key=lambda x: x[1], reverse=True)
    
    # Get top-k results
    top_results = similarities[:top_k]
    
    logger.info(f"\nTop {len(top_results)} results:")
    for i, (chunk, similarity) in enumerate(top_results):
        logger.info(f"\nResult {i+1} (similarity: {similarity:.4f}):")
        source = chunk["metadata"].get("source", "unknown") if "metadata" in chunk else "unknown"
        logger.info(f"Source: {source}")
        # Print first 150 chars as preview
        logger.info(f"Preview: {chunk['text'][:150]}...")
    
    # Format context for the prompt
    context_chunks = [chunk["text"] for chunk, _ in top_results]
    formatted_context = "\n\n".join([f"Context document {i+1}:\n{ctx}" for i, ctx in enumerate(context_chunks)])
    
    # Build the prompt with context
    prompt = f"""You are a helpful assistant with access to IBM Redbooks information. 
Use the following context to answer the question, and if the information is not in the context, say so.

{formatted_context}

Question: {query}

Answer:"""
    
    # Send request to Ollama
    logger.info("\nGenerating response from Ollama...")
    
    response = requests.post(
        f"{ollama_url}/api/generate",
        json={
            "model": model,
            "prompt": prompt,
            "temperature": temperature,
            "max_tokens": 800,
            "stream": False
        }
    )
    
    # Print response
    if response.status_code == 200:
        answer = response.json().get("response", "No response received")
        
        print("\n" + "="*80)
        print("QUERY:")
        print(query)
        print("\n" + "="*80)
        print("ANSWER:")
        print("="*80)
        print(answer)
        print("="*80)
    else:
        logger.error(f"Error getting response: {response.text}")

def main():
    parser = argparse.ArgumentParser(description="Test IBM Redbooks RAG with Ollama")
    parser.add_argument(
        "--input", "-i", 
        default="./processed_redbooks/ollama/redbooks_ollama.jsonl",
        help="Path to JSONL file with processed chunks"
    )
    parser.add_argument(
        "--model", "-m", 
        default="llama3",
        help="Ollama model to use"
    )
    parser.add_argument(
        "--host", 
        default="localhost",
        help="Ollama host"
    )
    parser.add_argument(
        "--port", "-p", 
        type=int,
        default=11434,
        help="Ollama port"
    )
    parser.add_argument(
        "--query", "-q",
        required=True,
        help="Query to test"
    )
    parser.add_argument(
        "--top-k", "-k",
        type=int,
        default=3,
        help="Number of top results to use for context"
    )
    parser.add_argument(
        "--temperature", "-t",
        type=float,
        default=0.7,
        help="Model temperature"
    )
    
    args = parser.parse_args()
    
    test_ollama_rag(
        query=args.query,
        jsonl_file=Path(args.input),
        model=args.model,
        host=args.host,
        port=args.port,
        top_k=args.top_k,
        temperature=args.temperature
    )

if __name__ == "__main__":
    main()
