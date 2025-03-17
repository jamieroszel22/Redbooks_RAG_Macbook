import argparse
import json
import logging
import os
import re
import requests
import time
from pathlib import Path
from typing import List, Dict, Any
import numpy as np
from tqdm import tqdm
from colorama import init, Fore, Style

# Initialize colorama for colored terminal output
init()

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Ollama API settings
OLLAMA_BASE_URL = "http://localhost:11434/api"
DEFAULT_MODEL = "granite3.2:8b-instruct-fp16"

class OllamaRAG:
    def __init__(self, chunks_dir: str, ollama_dir: str, model: str = DEFAULT_MODEL):
        self.chunks_dir = Path(chunks_dir)
        self.ollama_dir = Path(ollama_dir)
        self.model = model
        self.chunks = []
        self.embeddings = []
        self.documents = set()
        
        # System prompt for technical content
        self.system_prompt = """You are an IBM technical expert assistant designed to help with complex IBM technologies and products.
Your responses must be:
1. Technically accurate and precise
2. Based only on the provided context - do not invent information
3. Clear and concise, using professional language
4. Structured with appropriate headings and bullet points when relevant
5. Free of marketing language and sales pitches

When responding to queries:
- If you don't have enough information in the context, acknowledge limitations clearly
- For commands or code examples, use proper code formatting
- Prioritize information relevant to the query rather than general information
- Cite specific IBM Redbooks or documentation when possible from the context

Your goal is to provide technically precise assistance with IBM technologies."""
    
    def check_ollama_available(self) -> bool:
        """Check if Ollama server is running."""
        try:
            response = requests.get(f"{OLLAMA_BASE_URL}/tags")
            return response.status_code == 200
        except requests.RequestException:
            return False
    
    def load_chunks(self) -> None:
        """Load all chunks from the chunks directory."""
        self.chunks = []
        chunk_files = list(self.chunks_dir.glob("*/*chunk_*.txt"))
        
        # Sort files for consistent loading
        chunk_files.sort()
        
        for chunk_file in tqdm(chunk_files, desc="Loading chunks"):
            doc_name = chunk_file.parent.name
            self.documents.add(doc_name)
            
            with open(chunk_file, 'r', encoding='utf-8') as f:
                content = f.read()
                self.chunks.append({
                    "document": doc_name,
                    "id": chunk_file.stem,
                    "content": content,
                    "file_path": str(chunk_file)
                })
        
        logger.info(f"Loaded {len(self.chunks)} chunks from {len(self.documents)} documents")
    
    def generate_embeddings(self) -> None:
        """Generate embeddings for all chunks using Ollama."""
        if not self.chunks:
            logger.error("No chunks loaded. Call load_chunks() first.")
            return
        
        embedding_cache_file = self.ollama_dir / f"embeddings_cache_{self.model.replace(':', '_')}.json"
        
        # Check if embeddings cache exists
        if embedding_cache_file.exists():
            try:
                with open(embedding_cache_file, 'r', encoding='utf-8') as f:
                    cache_data = json.load(f)
                    
                    # Validate cache structure
                    if "model" in cache_data and cache_data["model"] == self.model and "embeddings" in cache_data:
                        logger.info(f"Loading embeddings from cache ({len(cache_data['embeddings'])} embeddings)")
                        
                        # Check if cache has all current chunks
                        cache_ids = {item["id"] for item in cache_data["embeddings"]}
                        current_ids = {chunk["id"] for chunk in self.chunks}
                        
                        if cache_ids.issuperset(current_ids):
                            # Cache is complete
                            self.embeddings = cache_data["embeddings"]
                            logger.info("Using cached embeddings")
                            return
                        else:
                            logger.info(f"Cache is incomplete. Missing {len(current_ids - cache_ids)} chunks. Regenerating all embeddings.")
            except Exception as e:
                logger.error(f"Error loading embeddings cache: {str(e)}")
        
        # Generate embeddings for all chunks
        self.embeddings = []
        
        for chunk in tqdm(self.chunks, desc="Generating embeddings"):
            try:
                # Call Ollama Embeddings API
                response = requests.post(
                    f"{OLLAMA_BASE_URL}/embeddings",
                    json={"model": self.model, "prompt": chunk["content"]}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    self.embeddings.append({
                        "id": chunk["id"],
                        "document": chunk["document"],
                        "embedding": data["embedding"],
                        "file_path": chunk["file_path"]
                    })
                else:
                    logger.error(f"Error generating embedding for {chunk['id']}: {response.text}")
            except Exception as e:
                logger.error(f"Exception generating embedding for {chunk['id']}: {str(e)}")
        
        # Save embeddings to cache
        try:
            with open(embedding_cache_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "model": self.model,
                    "date_generated": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "embeddings": self.embeddings
                }, f)
            logger.info(f"Saved {len(self.embeddings)} embeddings to cache")
        except Exception as e:
            logger.error(f"Error saving embeddings cache: {str(e)}")
    
    def prepare_for_ollama(self) -> None:
        """Prepare data for Ollama by creating JSONL files."""
        if not self.chunks:
            logger.error("No chunks loaded. Call load_chunks() first.")
            return
        
        # Create JSONL file for each document
        for document in self.documents:
            doc_chunks = [chunk for chunk in self.chunks if chunk["document"] == document]
            
            if not doc_chunks:
                continue
            
            jsonl_file = self.ollama_dir / f"{document}.jsonl"
            
            with open(jsonl_file, 'w', encoding='utf-8') as f:
                for chunk in doc_chunks:
                    entry = {
                        "text": chunk["content"],
                        "metadata": {
                            "source": chunk["file_path"],
                            "chunk_id": chunk["id"]
                        }
                    }
                    f.write(json.dumps(entry, ensure_ascii=False) + "\n")
            
            logger.info(f"Created {jsonl_file} with {len(doc_chunks)} chunks")
        
        # Create a combined JSONL file with all chunks
        combined_file = self.ollama_dir / "all_redbooks.jsonl"
        with open(combined_file, 'w', encoding='utf-8') as f:
            for chunk in self.chunks:
                entry = {
                    "text": chunk["content"],
                    "metadata": {
                        "source": chunk["file_path"],
                        "document": chunk["document"],
                        "chunk_id": chunk["id"]
                    }
                }
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        
        logger.info(f"Created combined file {combined_file} with {len(self.chunks)} chunks")
    
    def vector_search(self, query: str, num_results: int = 5) -> List[Dict[str, Any]]:
        """Perform vector search for a query."""
        if not self.embeddings:
            logger.error("No embeddings available. Call generate_embeddings() first.")
            return []
        
        try:
            # Get embedding for the query
            response = requests.post(
                f"{OLLAMA_BASE_URL}/embeddings",
                json={"model": self.model, "prompt": query}
            )
            
            if response.status_code != 200:
                logger.error(f"Error getting query embedding: {response.text}")
                return []
            
            query_embedding = response.json()["embedding"]
            
            # Calculate cosine similarity with all embeddings
            similarities = []
            for i, item in enumerate(self.embeddings):
                chunk_embedding = item["embedding"]
                similarity = self.cosine_similarity(query_embedding, chunk_embedding)
                similarities.append((i, similarity))
            
            # Sort by similarity (highest first)
            similarities.sort(key=lambda x: x[1], reverse=True)
            
            # Get top results
            top_results = []
            for i, sim in similarities[:num_results]:
                embedding_item = self.embeddings[i]
                
                # Find the corresponding chunk
                chunk = next((c for c in self.chunks if c["id"] == embedding_item["id"]), None)
                
                if chunk:
                    top_results.append({
                        "chunk": chunk,
                        "similarity": sim
                    })
            
            return top_results
        
        except Exception as e:
            logger.error(f"Error in vector search: {str(e)}")
            return []
    
    def cosine_similarity(self, vec1, vec2):
        """Calculate cosine similarity between two vectors."""
        vec1 = np.array(vec1)
        vec2 = np.array(vec2)
        return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
    
    def query_ollama(self, query: str, context: str = "") -> str:
        """Query Ollama with RAG context."""
        try:
            payload = {
                "model": self.model,
                "prompt": query,
                "system": self.system_prompt,
                "stream": False
            }
            
            if context:
                payload["context"] = [
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": "Here is some context information:\n\n" + context}
                ]
            
            response = requests.post(
                f"{OLLAMA_BASE_URL}/chat",
                json=payload
            )
            
            if response.status_code == 200:
                return response.json()["message"]["content"]
            else:
                logger.error(f"Error querying Ollama: {response.status_code} - {response.text}")
                return f"Error querying the model. Status code: {response.status_code}"
        
        except Exception as e:
            logger.error(f"Exception querying Ollama: {str(e)}")
            return f"Error: {str(e)}"
    
    def interactive_query(self) -> None:
        """Run an interactive RAG query session."""
        if not self.check_ollama_available():
            print(f"{Fore.RED}Error: Ollama server not available. Make sure it's running at {OLLAMA_BASE_URL}{Style.RESET_ALL}")
            logger.error(f"Ollama server not available at {OLLAMA_BASE_URL}")
            return
        
        if not self.chunks:
            print("Loading chunks...")
            self.load_chunks()
        
        if not self.embeddings:
            print("Generating embeddings. This may take a while...")
            self.generate_embeddings()
        
        print(f"{Fore.GREEN}=== IBM Redbooks RAG System with {self.model} ==={Style.RESET_ALL}")
        print(f"Loaded {len(self.chunks)} chunks from {len(self.documents)} documents")
        print("Type 'exit' or 'quit' to end the session")
        
        while True:
            query = input(f"\n{Fore.BLUE}Enter your query: {Style.RESET_ALL}")
            
            if query.lower() in ['exit', 'quit']:
                print("Exiting RAG system. Goodbye!")
                break
            
            if not query.strip():
                continue
            
            # Find relevant chunks
            print("Searching for relevant context...")
            results = self.vector_search(query, num_results=3)
            
            if not results:
                print(f"{Fore.YELLOW}No relevant context found. Querying without context...{Style.RESET_ALL}")
                response = self.query_ollama(query)
            else:
                # Combine context from top results
                context = "\n\n---\n\n".join([r["chunk"]["content"] for r in results])
                
                # Show sources
                print(f"{Fore.GREEN}Found {len(results)} relevant chunks:{Style.RESET_ALL}")
                for i, result in enumerate(results):
                    doc_name = result["chunk"]["document"]
                    similarity = result["similarity"] * 100
                    print(f"  {i+1}. {doc_name} (similarity: {similarity:.1f}%)")
                
                # Query with context
                response = self.query_ollama(query, context)
            
            # Display response
            print(f"\n{Fore.CYAN}=== Response ==={Style.RESET_ALL}")
            print(response)

def main():
    parser = argparse.ArgumentParser(description="Ollama RAG Integration for IBM Redbooks")
    parser.add_argument("--data_dir", type=str, default="C:\\Users\\jamie\\OneDrive\\Documents\\Redbooks RAG", 
                        help="Base directory for data storage")
    parser.add_argument("--model", type=str, default=DEFAULT_MODEL, 
                        help=f"Ollama model to use (default: {DEFAULT_MODEL})")
    parser.add_argument("--prepare", action="store_true", 
                        help="Prepare data for Ollama without starting interactive query")
    args = parser.parse_args()
    
    chunks_dir = Path(args.data_dir) / "processed_redbooks" / "chunks"
    ollama_dir = Path(args.data_dir) / "processed_redbooks" / "ollama"
    
    if not chunks_dir.exists():
        logger.error(f"Chunks directory not found: {chunks_dir}")
        print(f"Error: Chunks directory not found. Please process PDFs first using redbook-processor.py")
        return
    
    # Create Ollama directory if it doesn't exist
    ollama_dir.mkdir(parents=True, exist_ok=True)
    
    rag = OllamaRAG(chunks_dir, ollama_dir, args.model)
    
    # Check if Ollama is available
    if not rag.check_ollama_available():
        print(f"{Fore.RED}Error: Ollama server not available. Make sure it's running at {OLLAMA_BASE_URL}{Style.RESET_ALL}")
        logger.error(f"Ollama server not available at {OLLAMA_BASE_URL}")
        return
    
    # Load chunks
    print("Loading chunks...")
    rag.load_chunks()
    
    # Prepare data for Ollama
    print("Preparing data for Ollama...")
    rag.prepare_for_ollama()
    
    if args.prepare:
        print(f"{Fore.GREEN}Data preparation complete. Files saved to {ollama_dir}{Style.RESET_ALL}")
        return
    
    # Generate embeddings
    print("Generating embeddings. This may take a while...")
    rag.generate_embeddings()
    
    # Start interactive query
    rag.interactive_query()

if __name__ == "__main__":
    main()
