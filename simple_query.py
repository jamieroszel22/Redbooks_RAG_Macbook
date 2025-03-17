import argparse
import os
import json
import logging
from pathlib import Path
import re
from operator import itemgetter
from colorama import init, Fore, Style

# Initialize colorama for colored terminal output
init()

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def load_chunks(chunks_dir):
    """Load all chunk files from the chunks directory."""
    chunks = []
    chunk_files = list(Path(chunks_dir).glob("*/*chunk_*.txt"))
    
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

def search_chunks(chunks, query, num_results=5):
    """Search for chunks that match the query terms."""
    # Break query into terms
    query_terms = re.findall(r'\b\w+\b', query.lower())
    
    # Score each chunk based on term frequency
    scored_chunks = []
    for chunk in chunks:
        content = chunk["content"].lower()
        score = 0
        
        # Count occurrences of each term
        for term in query_terms:
            term_count = len(re.findall(r'\b' + re.escape(term) + r'\b', content))
            score += term_count
        
        # Only include chunks with at least one match
        if score > 0:
            scored_chunks.append((chunk, score))
    
    # Sort by score in descending order
    scored_chunks.sort(key=itemgetter(1), reverse=True)
    
    return [chunk for chunk, score in scored_chunks[:num_results]]

def highlight_terms(text, terms):
    """Highlight search terms in the text."""
    highlighted = text
    for term in terms:
        pattern = re.compile(r'\b(' + re.escape(term) + r')\b', re.IGNORECASE)
        highlighted = pattern.sub(Fore.YELLOW + r'\1' + Style.RESET_ALL, highlighted)
    
    return highlighted

def interactive_query(chunks_dir):
    """Run an interactive query session."""
    chunks = load_chunks(chunks_dir)
    
    print(f"{Fore.GREEN}=== IBM Redbooks Simple RAG Query System ==={Style.RESET_ALL}")
    print(f"Loaded {len(chunks)} chunks from {len(set([c['document'] for c in chunks]))} documents")
    print("Type 'exit' or 'quit' to end the session")
    
    while True:
        query = input(f"\n{Fore.BLUE}Enter your query: {Style.RESET_ALL}")
        
        if query.lower() in ['exit', 'quit']:
            print("Exiting query system. Goodbye!")
            break
        
        if not query.strip():
            continue
        
        # Search for relevant chunks
        results = search_chunks(chunks, query)
        
        if not results:
            print(f"{Fore.RED}No results found for your query.{Style.RESET_ALL}")
            continue
        
        # Display results
        print(f"\n{Fore.GREEN}Found {len(results)} relevant chunks:{Style.RESET_ALL}\n")
        
        query_terms = re.findall(r'\b\w+\b', query.lower())
        
        for i, result in enumerate(results):
            print(f"{Fore.CYAN}Result {i+1} from {result['document']}{Style.RESET_ALL}")
            
            # Highlight the query terms in the content
            highlighted_content = highlight_terms(result["content"], query_terms)
            
            # Truncate if too long
            if len(highlighted_content) > 500:
                # Try to find a good breaking point
                break_point = highlighted_content.rfind(".", 400, 500)
                if break_point == -1:
                    break_point = 500
                print(highlighted_content[:break_point+1] + "...")
            else:
                print(highlighted_content)
            
            print(f"Source: {result['file_path']}")
            print("-" * 80)

def main():
    parser = argparse.ArgumentParser(description="Simple RAG Query System for IBM Redbooks")
    parser.add_argument("--data_dir", type=str, default="C:\\Users\\jamie\\OneDrive\\Documents\\Redbooks RAG", 
                        help="Base directory for data storage")
    args = parser.parse_args()
    
    chunks_dir = Path(args.data_dir) / "processed_redbooks" / "chunks"
    
    if not chunks_dir.exists():
        logger.error(f"Chunks directory not found: {chunks_dir}")
        print(f"Error: Chunks directory not found. Please process PDFs first using redbook-processor.py")
        return
    
    interactive_query(chunks_dir)

if __name__ == "__main__":
    main()
