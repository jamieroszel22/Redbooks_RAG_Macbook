import argparse
import logging
import os
import time
from pathlib import Path
from typing import List, Optional, Tuple

# Configure logging first
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("redbook-processor")

# Check for GPU availability
import torch
if torch.cuda.is_available():
    logger.info(f"GPU found: {torch.cuda.get_device_name(0)}")
    logger.info(f"Using CUDA version: {torch.version.cuda}")
else:
    logger.info("No GPU found, using CPU. This might be slower.")

try:
    from docling.document_converter import DocumentConverter, PdfFormatOption
    from docling.datamodel.pipeline_options import PdfPipelineOptions
    from docling.datamodel.base_models import InputFormat, ConversionStatus
    from docling_core.types.doc import ImageRefMode
except ImportError:
    logger.error("Docling library not found. Please install it with: pip install docling")
    exit(1)

def process_redbooks(
    input_paths: List[str],
    output_dir: Path,
    chunk_size: Optional[int] = None,
    enable_ocr: bool = True,
    debug_mode: bool = False
) -> Tuple[int, int, int]:
    """
    Process IBM Redbooks PDFs and prepare them for RAG.
    
    Args:
        input_paths: List of paths to IBM Redbook PDFs
        output_dir: Directory to save processed outputs
        chunk_size: Optional size for text chunking (if needed)
        enable_ocr: Whether to enable OCR for scanned content
        debug_mode: Enable debug visualizations
        
    Returns:
        Tuple of (success_count, partial_success_count, failure_count)
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Configure PDF processing options - Simpler version that should work with most Docling versions
    pipeline_options = PdfPipelineOptions()
    
    # Enable debug visualizations if requested
    if debug_mode:
        try:
            from docling.datamodel.settings import settings
            settings.debug.visualize_layout = True
            settings.debug.visualize_ocr = True
            settings.debug.visualize_tables = True
        except (ImportError, AttributeError):
            logger.warning("Could not enable debug visualizations. This might be due to a different Docling version.")
    
    # Create document converter
    doc_converter = DocumentConverter(
        format_options={
            InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
        }
    )
    
    start_time = time.time()
    logger.info(f"Starting to process {len(input_paths)} IBM Redbooks...")
    
    # Process each document
    input_path_objects = [Path(p) for p in input_paths]
    results = doc_converter.convert_all(
        input_path_objects,
        raises_on_error=False,  # Continue processing even if some files fail
    )
    
    # Track statistics
    success_count = 0
    partial_success_count = 0
    failure_count = 0
    
    # Process results
    for result in results:
        if result.status == ConversionStatus.SUCCESS:
            success_count += 1
            doc_filename = result.input.file.stem
            output_path = output_dir / doc_filename
            output_path.mkdir(exist_ok=True)
            
            logger.info(f"Successfully processed: {doc_filename}")
            
            # Save as Markdown (good for many RAG systems)
            result.document.save_as_markdown(
                output_path / f"{doc_filename}.md",
                image_mode=ImageRefMode.PLACEHOLDER,
            )
            
            # Save as plain text (most compatible format)
            result.document.save_as_markdown(
                output_path / f"{doc_filename}.txt",
                image_mode=ImageRefMode.PLACEHOLDER,
                strict_text=True,
            )
            
            # Save structured JSON (preserves more document features)
            result.document.save_as_json(
                output_path / f"{doc_filename}.json",
                image_mode=ImageRefMode.PLACEHOLDER,
            )
            
            # Save as HTML (useful for viewing with formatting)
            result.document.save_as_html(
                output_path / f"{doc_filename}.html",
                image_mode=ImageRefMode.EMBEDDED if debug_mode else ImageRefMode.PLACEHOLDER,
            )
            
            # Optional: Save document tokens format (can be useful for specific NLP tasks)
            if debug_mode:
                result.document.save_as_document_tokens(
                    output_path / f"{doc_filename}.doctags.txt"
                )
            
        elif result.status == ConversionStatus.PARTIAL_SUCCESS:
            partial_success_count += 1
            logger.warning(f"Partial success for: {result.input.file}")
            if result.errors:
                for error in result.errors:
                    logger.warning(f"  Error: {error.error_message}")
        else:
            failure_count += 1
            logger.error(f"Failed to process: {result.input.file}")
            if result.errors:
                for error in result.errors:
                    logger.error(f"  Error: {error.error_message}")
    
    total_time = time.time() - start_time
    logger.info(f"Processing complete. {success_count}/{len(input_paths)} documents processed successfully in {total_time:.2f} seconds.")
    logger.info(f"  - Partially successful: {partial_success_count}")
    logger.info(f"  - Failed: {failure_count}")
    
    return success_count, partial_success_count, failure_count

def create_chunks_for_rag(
    docs_dir: Path,
    output_dir: Path,
    chunk_size: int = 1000,
    chunk_overlap: int = 200
) -> int:
    """
    Create text chunks from processed documents for RAG.
    Uses a memory-efficient approach for large documents.
    
    Args:
        docs_dir: Directory containing processed documents
        output_dir: Directory to save chunked outputs
        chunk_size: Size of chunks in characters
        chunk_overlap: Overlap between chunks in characters
        
    Returns:
        Number of chunks created
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        # Try to import the text splitter from docling_core
        from docling_core.chunking.text_splitter import TextSplitter
        use_docling_splitter = True
    except ImportError:
        # Fallback to a simple implementation if not available
        logger.warning("Could not import TextSplitter from docling_core. Using a simple chunking implementation.")
        use_docling_splitter = False
    
    # Track total chunks
    total_chunks = 0
    
    # Process all text files in the docs directory and subdirectories
    for txt_file in docs_dir.glob("**/*.txt"):
        rel_path = txt_file.relative_to(docs_dir)
        output_subdir = output_dir / rel_path.parent
        output_subdir.mkdir(parents=True, exist_ok=True)
        
        # Create chunks directory upfront
        chunks_dir = output_subdir / f"{txt_file.stem}_chunks"
        chunks_dir.mkdir(exist_ok=True)
        
        # Get file size to decide on chunking strategy
        file_size = txt_file.stat().st_size
        logger.info(f"File size: {file_size / (1024*1024):.2f} MB - {txt_file}")
        
        # Write chunks file header
        chunk_file = output_subdir / f"{txt_file.stem}_chunks.txt"
        with open(chunk_file, "w", encoding="utf-8") as f:
            f.write(f"# Chunks from {txt_file}\n\n")
        
        # Use memory-efficient chunking for large files
        if file_size > 10 * 1024 * 1024:  # 10MB threshold
            logger.info(f"Using streaming approach for large file: {txt_file}")
            
            chunk_count = stream_chunks_from_file(
                txt_file, 
                chunks_dir, 
                chunk_file,
                chunk_size, 
                chunk_overlap
            )
            logger.info(f"Created {chunk_count} chunks from large file {txt_file}")
            total_chunks += chunk_count
        else:
            # For smaller files, we can load the whole content
            with open(txt_file, "r", encoding="utf-8") as f:
                text = f.read()
            
            # Create chunks using appropriate method
            if use_docling_splitter:
                text_splitter = TextSplitter(
                    chunk_size=chunk_size,
                    chunk_overlap=chunk_overlap
                )
                chunks = text_splitter.split_text(text)
            else:
                # Memory-efficient chunking for smaller files
                chunks = []
                start = 0
                
                while start < len(text):
                    # Extract a chunk
                    end = min(start + chunk_size, len(text))
                    
                    # If not at the end, try to find a good break point
                    if end < len(text):
                        # Try to find end of sentence or paragraph
                        for sep in ["\n\n", "\n", ". ", "! ", "? "]:
                            pos = text.rfind(sep, start, end)
                            if pos != -1:
                                end = pos + len(sep)
                                break
                    
                    # Add the chunk
                    chunks.append(text[start:end])
                    
                    # Move to next chunk with overlap
                    start = max(start + 1, end - chunk_overlap) if end < len(text) else end
            
            # Append to chunks file
            with open(chunk_file, "a", encoding="utf-8") as f:
                for i, chunk in enumerate(chunks):
                    f.write(f"--- Chunk {i+1} ---\n")
                    f.write(chunk)
                    f.write("\n\n")
            
            # Create individual chunk files
            for i, chunk in enumerate(chunks):
                with open(chunks_dir / f"chunk_{i+1:04d}.txt", "w", encoding="utf-8") as f:
                    f.write(chunk)
            
            logger.info(f"Created {len(chunks)} chunks from {txt_file}")
            total_chunks += len(chunks)
    
    logger.info(f"Chunking complete. Created {total_chunks} total chunks.")
    return total_chunks

def stream_chunks_from_file(
    input_file: Path, 
    chunks_dir: Path, 
    summary_file: Path,
    chunk_size: int = 1000, 
    chunk_overlap: int = 200
) -> int:
    """
    Process a large file in streaming fashion, without loading it all at once.
    
    Args:
        input_file: Path to the input text file
        chunks_dir: Directory to save individual chunks
        summary_file: File to append chunk summaries
        chunk_size: Size of chunks in characters
        chunk_overlap: Overlap between chunks in characters
        
    Returns:
        Number of chunks created
    """
    chunk_count = 0
    buffer = ""
    chunk_buffer = []
    
    with open(input_file, "r", encoding="utf-8") as in_file, \
         open(summary_file, "a", encoding="utf-8") as summary:
        
        # Read file in blocks to avoid loading it all at once
        while True:
            # Read a block that's larger than our chunk size
            block = in_file.read(chunk_size * 2)  
            if not block:
                break
                
            # Add to our text buffer
            buffer += block
            
            # Process complete chunks while we have enough text
            while len(buffer) >= chunk_size:
                # Get a chunk-sized piece of text
                chunk_text = buffer[:chunk_size]
                
                # Find a good breaking point if not at EOF
                if len(buffer) > chunk_size:
                    # Try to find natural break points
                    break_point = chunk_size
                    for sep in ["\n\n", "\n", ". ", "! ", "? "]:
                        pos = chunk_text.rfind(sep)
                        if pos > chunk_size // 2:  # Don't break too early
                            break_point = pos + len(sep)
                            break
                    
                    chunk_text = buffer[:break_point]
                    
                    # Keep overlap for next chunk
                    buffer = buffer[max(0, break_point - chunk_overlap):]
                else:
                    # If we're at the end, use all remaining text
                    buffer = ""
                
                # Increment chunk count
                chunk_count += 1
                
                # Write individual chunk file
                with open(chunks_dir / f"chunk_{chunk_count:04d}.txt", "w", encoding="utf-8") as f:
                    f.write(chunk_text)
                
                # Add to summary file
                summary.write(f"--- Chunk {chunk_count} ---\n")
                # Write a preview of the chunk (first 100 chars)
                summary.write(f"{chunk_text[:100]}...\n\n")
                
                # Store chunk for Ollama preparation
                chunk_buffer.append(chunk_text)
                
                # Flush every 10 chunks to avoid memory buildup
                if len(chunk_buffer) >= 10:
                    chunk_buffer = []
    
    # Handle any remaining text
    if buffer:
        chunk_count += 1
        with open(chunks_dir / f"chunk_{chunk_count:04d}.txt", "w", encoding="utf-8") as f:
            f.write(buffer)
        
        with open(summary_file, "a", encoding="utf-8") as summary:
            summary.write(f"--- Chunk {chunk_count} ---\n")
            summary.write(f"{buffer[:100]}...\n\n")
    
    return chunk_count

def prepare_for_ollama(
    chunks_dir: Path,
    output_file: Path,
    include_metadata: bool = True,
    max_chunks_in_memory: int = 1000  # Limit memory usage
) -> int:
    """
    Prepare chunked content for Ollama integration.
    Uses a streaming approach for large numbers of chunks.
    
    Args:
        chunks_dir: Directory containing chunks
        output_file: Output JSONL file for Ollama
        include_metadata: Whether to include metadata
        max_chunks_in_memory: Maximum number of chunks to process at once
    
    Returns:
        Number of records written
    """
    import json
    import re
    from datetime import datetime
    
    # Make sure the output directory exists
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Find all chunk files but exclude summary files
    # Only look for files matching the pattern chunk_XXXX.txt
    chunk_files = []
    for pattern in ["**/chunk_*.txt", "**/*chunks/chunk_*.txt"]:
        chunk_files.extend(list(chunks_dir.glob(pattern)))
    
    if not chunk_files:
        logger.warning(f"No chunk files found in {chunks_dir}")
        return 0
    
    logger.info(f"Processing {len(chunk_files)} chunk files for Ollama")
    
    # Process in batches to limit memory usage
    total_records = 0
    batch_size = min(max_chunks_in_memory, len(chunk_files))
    
    # Open the output file in append mode
    with open(output_file, "w", encoding="utf-8") as f:
        # Process in batches
        for i in range(0, len(chunk_files), batch_size):
            batch_end = min(i + batch_size, len(chunk_files))
            logger.info(f"Processing batch {i//batch_size + 1}/{(len(chunk_files) + batch_size - 1)//batch_size}: chunks {i+1}-{batch_end}")
            
            # Process this batch
            for j in range(i, batch_end):
                chunk_file = chunk_files[j]
                
                try:
                    # Read chunk content
                    with open(chunk_file, "r", encoding="utf-8") as chunk_f:
                        content = chunk_f.read().strip()
                    
                    if not content:
                        continue
                    
                    # Extract metadata from path
                    # Handle different directory structures
                    if "_chunks" in str(chunk_file.parent):
                        doc_name = chunk_file.parent.name.replace("_chunks", "")
                    else:
                        # Find the parent document name from the path
                        parent_parts = list(chunk_file.parts)
                        for i, part in enumerate(parent_parts):
                            if "chunks" in part:
                                if i > 0:
                                    doc_name = parent_parts[i-1]
                                    break
                        else:
                            # Fallback if we can't find the document name
                            doc_name = "unknown"
                    
                    # Extract chunk number using regex to be safer
                    chunk_match = re.search(r'chunk_(\d+)', chunk_file.stem)
                    if chunk_match:
                        chunk_num = int(chunk_match.group(1))
                    else:
                        chunk_num = 0
                    
                    # Create record
                    record = {
                        "text": content,
                        "metadata": {
                            "source": doc_name,
                            "chunk": chunk_num,
                            "processed_date": datetime.now().isoformat(),
                            "file_path": str(chunk_file)
                        } if include_metadata else {}
                    }
                    
                    # Write record to JSONL file
                    f.write(json.dumps(record) + "\n")
                    total_records += 1
                    
                except Exception as e:
                    logger.error(f"Error processing chunk file {chunk_file}: {e}")
                    logger.error(f"Exception details: {type(e).__name__}: {str(e)}")
    
    logger.info(f"Created {total_records} records for Ollama in {output_file}")
    return total_records

def main():
    parser = argparse.ArgumentParser(description="Process IBM Redbooks for RAG using Docling")
    parser.add_argument(
        "--input", "-i", 
        nargs="+", 
        required=True,
        help="Paths to IBM Redbook PDFs or directory containing PDFs"
    )
    parser.add_argument(
        "--output", "-o", 
        default="./processed_redbooks",
        help="Output directory for processed files"
    )
    parser.add_argument(
        "--chunk-size", 
        type=int, 
        default=1000,
        help="Size of text chunks in characters"
    )
    parser.add_argument(
        "--chunk-overlap", 
        type=int, 
        default=200,
        help="Overlap between chunks in characters"
    )
    parser.add_argument(
        "--enable-ocr", 
        action="store_true",
        help="Enable OCR for scanned content"
    )
    parser.add_argument(
        "--debug", 
        action="store_true",
        help="Enable debug mode with visualizations"
    )
    parser.add_argument(
        "--skip-chunking", 
        action="store_true",
        help="Skip chunking step"
    )
    parser.add_argument(
        "--prepare-ollama", 
        action="store_true",
        help="Prepare output for Ollama"
    )
    
    args = parser.parse_args()
    
    # Process input paths (handle directories)
    input_paths = []
    for path in args.input:
        path_obj = Path(path)
        if path_obj.is_dir():
            # Add all PDFs in the directory
            input_paths.extend([str(pdf) for pdf in path_obj.glob("**/*.pdf")])
        else:
            input_paths.append(str(path_obj))
    
    if not input_paths:
        logger.error("No PDF files found in the specified input paths.")
        return
    
    # Create output directories
    output_dir = Path(args.output)
    docs_dir = output_dir / "docs"
    chunks_dir = output_dir / "chunks"
    ollama_dir = output_dir / "ollama"
    
    # Process Redbooks
    success_count, partial_count, failure_count = process_redbooks(
        input_paths=input_paths,
        output_dir=docs_dir,
        chunk_size=args.chunk_size,
        enable_ocr=args.enable_ocr,
        debug_mode=args.debug
    )
    
    # Create chunks if requested
    if not args.skip_chunking and success_count > 0:
        total_chunks = create_chunks_for_rag(
            docs_dir=docs_dir,
            output_dir=chunks_dir,
            chunk_size=args.chunk_size,
            chunk_overlap=args.chunk_overlap
        )
        
        # Prepare for Ollama if requested
        if args.prepare_ollama and total_chunks > 0:
            ollama_dir.mkdir(exist_ok=True)
            prepare_for_ollama(
                chunks_dir=chunks_dir,
                output_file=ollama_dir / "redbooks_ollama.jsonl"
            )
    
    logger.info("Processing complete!")
    logger.info(f"Processed documents are in: {docs_dir}")
    if not args.skip_chunking:
        logger.info(f"Chunked content is in: {chunks_dir}")
    if args.prepare_ollama:
        logger.info(f"Ollama-ready files are in: {ollama_dir}")

if __name__ == "__main__":
    main()
