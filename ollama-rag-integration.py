import argparse
import json
import logging
import os
from pathlib import Path
from typing import List, Dict, Any, Optional

import requests

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("ollama-rag")

class OllamaRAG:
    def __init__(
        self, 
        ollama_base_url: str = "http://localhost:11434",
        model: str = "llama3"
    ):
        """
        Initialize Ollama RAG integration.
        
        Args:
            ollama_base_url: Base URL for Ollama API
            model: Ollama model to use
        """
        self.base_url = ollama_base_url
        self.model = model
        
    def create_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for a list of texts using Ollama.
        
        Args:
            texts: List of text strings to embed
            
        Returns:
            List of embedding vectors
        """
        embeddings = []
        
        # First, test if model exists by trying to get embeddings for a sample text
        try:
            test_response = requests.post(
                f"{self.base_url}/api/embeddings",
                json={"model": self.model, "prompt": "Test"}
            )
            
            if test_response.status_code != 200:
                error_msg = test_response.text
                if "model not found" in error_msg.lower():
                    logger.error(f"Model '{self.model}' not found. Please pull it with 'ollama pull {self.model}'")
                    logger.error(f"Alternatively, specify a different model with --model")
                    logger.error(f"Available models can be listed with 'ollama list'")
                    return embeddings
                else:
                    logger.error(f"Error connecting to Ollama: {error_msg}")
                    return embeddings
        except Exception as e:
            logger.error(f"Error connecting to Ollama service: {e}")
            logger.error("Make sure Ollama is running with 'ollama serve'")
            return embeddings
            
        # If we get here, model exists and service is running
        for i, text in enumerate(texts):
            if i % 10 == 0:
                logger.info(f"Generating embedding {i+1}/{len(texts)}")
                
            try:
                response = requests.post(
                    f"{self.base_url}/api/embeddings",
                    json={"model": self.model, "prompt": text}
                )
                
                if response.status_code != 200:
                    logger.error(f"Error generating embedding: {response.text}")
                    continue
                    
                embedding = response.json().get("embedding")
                if embedding:
                    embeddings.append(embedding)
            except Exception as e:
                logger.error(f"Exception while generating embedding: {e}")
                continue
                
        return embeddings
    
    def query_with_context(
        self, 
        query: str, 
        context: List[str],
        temperature: float = 0.7,
        max_tokens: int = 500
    ) -> str:
        """
        Query Ollama with context from retrieved documents.
        
        Args:
            query: User query
            context: List of context strings to include
            temperature: Generation temperature (0.0-1.0)
            max_tokens: Maximum tokens in response
            
        Returns:
            Generated response from Ollama
        """
        # Format context for the prompt
        formatted_context = "\n\n".join([f"Context document {i+1}:\n{ctx}" for i, ctx in enumerate(context)])
        
        # Build the prompt with context
        prompt = f"""You are a helpful assistant with access to IBM Redbooks information. 
Use the following context to answer the question, and if the information is not in the context, say so.

{formatted_context}

Question: {query}

Answer:"""
        
        # Send request to Ollama
        response = requests.post(
            f"{self.base_url}/api/generate",
            json={
                "model": self.model,
                "prompt": prompt,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "stream": False
            }
        )
        
        if response.status_code != 200:
            return f"Error: {response.text}"
            
        return response.json().get("response", "No response received")
    
def create_simple_vector_store(jsonl_file: Path, model: str = "llama3", host: str = "localhost", port: int = 11434) -> Dict[str, Any]:
    """
    Create a simple in-memory vector store from processed chunks.
    
    Args:
        jsonl_file: Path to JSONL file with chunks
        model: Ollama model to use for embeddings
        host: Ollama host
        port: Ollama port
        
    Returns:
        Dict containing vectors and metadata
    """
    ollama = OllamaRAG(ollama_base_url=f"http://{host}:{port}", model=model)
    chunks = []
    texts = []
    
    # Load chunks from JSONL file
    with open(jsonl_file, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            chunk = json.loads(line)
            chunks.append(chunk)
            texts.append(chunk["text"])
    
    logger.info(f"Loaded {len(chunks)} chunks from {jsonl_file}")
    
    # Generate embeddings
    logger.info("Generating embeddings (this may take a while)...")
    embeddings = ollama.create_embeddings(texts)
    
    logger.info(f"Created {len(embeddings)} embeddings")
    
    return {
        "chunks": chunks,
        "embeddings": embeddings
    }

def vector_search(
    query: str,
    vector_store: Dict[str, Any],
    ollama: OllamaRAG,
    top_k: int = 3
) -> List[Dict[str, Any]]:
    """
    Perform vector search to find relevant chunks.
    
    Args:
        query: User query
        vector_store: Vector store with chunks and embeddings
        ollama: OllamaRAG instance
        top_k: Number of top results to return
        
    Returns:
        List of relevant chunks
    """
    # Generate query embedding
    query_embedding = ollama.create_embeddings([query])[0]
    
    # Calculate cosine similarity with all embeddings
    import numpy as np
    from scipy.spatial.distance import cosine
    
    similarities = []
    for i, embedding in enumerate(vector_store["embeddings"]):
        # Calculate cosine similarity (1 - cosine distance)
        similarity = 1 - cosine(query_embedding, embedding)
        similarities.append((i, similarity))
    
    # Sort by similarity (descending)
    similarities.sort(key=lambda x: x[1], reverse=True)
    
    # Return top-k results
    results = []
    for i, similarity in similarities[:top_k]:
        chunk = vector_store["chunks"][i]
        results.append({
            "text": chunk["text"],
            "metadata": chunk.get("metadata", {}),
            "similarity": similarity
        })
    
    return results

def save_vector_store(vector_store: Dict[str, Any], output_file: Path):
    """Save vector store to disk."""
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(vector_store, f)
    logger.info(f"Saved vector store to {output_file}")

def load_vector_store(input_file: Path) -> Dict[str, Any]:
    """Load vector store from disk."""
    with open(input_file, "r", encoding="utf-8") as f:
        vector_store = json.load(f)
    logger.info(f"Loaded vector store from {input_file}")
    return vector_store

def main():
    parser = argparse.ArgumentParser(description="Ollama RAG integration for processed IBM Redbooks")
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
        "--save-vectors", "-s",
        action="store_true",
        help="Save vector store to disk"
    )
    parser.add_argument(
        "--load-vectors", "-l",
        help="Load vector store from disk instead of creating new one"
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
    
    args = parser.parse_args()
    
    # Initialize Ollama client
    ollama_url = f"http://{args.host}:{args.port}"
    ollama = OllamaRAG(ollama_base_url=ollama_url, model=args.model)
    
    # Load or create vector store
    if args.load_vectors:
        vector_store = load_vector_store(Path(args.load_vectors))
    else:
        vector_store = create_simple_vector_store(
            Path(args.input),
            model=args.model,
            host=args.host,
            port=args.port
        )
        if args.save_vectors:
            save_vector_store(
                vector_store, 
                Path(args.input).with_suffix(".vectors.json")
            )
    
    # Execute query or run interactive mode
    if args.query:
        # Single query mode
        logger.info(f"Executing query: {args.query}")
        results = vector_search(args.query, vector_store, ollama)
        
        logger.info(f"Found {len(results)} relevant chunks")
        for i, result in enumerate(results):
            logger.info(f"Result {i+1} (similarity: {result['similarity']:.4f}):")
            logger.info(f"Source: {result['metadata'].get('source', 'unknown')}")
            logger.info(f"Text snippet: {result['text'][:150]}...")
        
        # Generate response with context
        context_texts = [result["text"] for result in results]
        response = ollama.query_with_context(args.query, context_texts)
        
        print("\n" + "="*50)
        print("ANSWER:")
        print("="*50)
        print(response)
        print("="*50)
        
    elif args.interactive:
        # Interactive mode
        print("\nIBM Redbooks RAG with Ollama")
        print("Type 'quit' or 'exit' to end the session")
        
        while True:
            query = input("\nEnter your query: ")
            if query.lower() in ("quit", "exit"):
                break
                
            results = vector_search(query, vector_store, ollama)
            context_texts = [result["text"] for result in results]
            response = ollama.query_with_context(query, context_texts)
            
            print("\n" + "="*50)
            print("ANSWER:")
            print("="*50)
            print(response)
            print("="*50)
    else:
        logger.info("Vector store ready. Use --query or --interactive to run queries.")

if __name__ == "__main__":
    main()