import argparse
import logging
import os
import time
import sys
import shutil
import hashlib
from pathlib import Path
import json
from datetime import datetime
import torch
from tqdm import tqdm

# Import Docling
try:
    from docling.document_converter import DocumentConverter, PdfFormatOption
    from docling.datamodel.base_models import InputFormat
    from docling.datamodel.pipeline_options import PdfPipelineOptions
    from docling.datamodel.settings import settings
    from docling_core.types.doc import ImageRefMode
except ImportError:
    print("Error: Docling not installed. Please install with 'pip install docling'")
    sys.exit(1)

# Import GPU check
from check_gpu import check_gpu

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def setup_gpu_optimizations():
    """Set optimal PyTorch CUDA settings for better performance"""
    if torch.cuda.is_available():
        logger.info("Optimizing PyTorch CUDA settings")
        # Force PyTorch to use TF32 on Ampere and newer GPUs
        torch.backends.cuda.matmul.allow_tf32 = True
        torch.backends.cudnn.allow_tf32 = True
        
        # Enable cuDNN benchmarking for best performance
        torch.backends.cudnn.benchmark = True
        
        # Set environment variables for Docling
        os.environ["DOCLING_USE_GPU"] = "1"
        os.environ["DOCLING_DEVICE"] = "cuda"
        os.environ["CUDA_VISIBLE_DEVICES"] = "0"
        os.environ["TORCH_CUDA_ARCH_LIST"] = "7.0;7.5;8.0;8.6;8.9;9.0"  # Support most modern GPUs
        
        logger.info("PyTorch CUDA optimizations applied")
        return True
    return False

def get_file_hash(file_path):
    """Calculate MD5 hash of file to track changes"""
    hasher = hashlib.md5()
    with open(file_path, 'rb') as f:
        buf = f.read(65536)
        while len(buf) > 0:
            hasher.update(buf)
            buf = f.read(65536)
    return hasher.hexdigest()

def load_processing_manifest(manifest_file):
    """Load or create processing manifest to track processed files"""
    if manifest_file.exists():
        try:
            with open(manifest_file, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            logger.warning("Manifest file corrupted, creating new one")
    
    # Create default manifest
    manifest = {
        "processed_files": {},
        "last_update": datetime.now().isoformat()
    }
    
    # Create directory if needed
    manifest_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Save and return
    with open(manifest_file, 'w') as f:
        json.dump(manifest, f, indent=2)
    
    return manifest

def update_manifest(manifest, manifest_file, file_path, hash_value, success):
    """Update the processing manifest with file information"""
    manifest["processed_files"][str(file_path)] = {
        "hash": hash_value,
        "last_processed": datetime.now().isoformat(),
        "success": success
    }
    manifest["last_update"] = datetime.now().isoformat()
    
    with open(manifest_file, 'w') as f:
        json.dump(manifest, f, indent=2)

def setup_directories(base_dir):
    """Create necessary directories if they don't exist."""
    paths = {
        "pdfs": Path(base_dir) / "pdfs",
        "processed": Path(base_dir) / "processed_redbooks",
        "docs": Path(base_dir) / "processed_redbooks" / "docs",
        "chunks": Path(base_dir) / "processed_redbooks" / "chunks",
        "ollama": Path(base_dir) / "processed_redbooks" / "ollama",
        "openwebui": Path(base_dir) / "openwebui"
    }
    
    for name, path in paths.items():
        path.mkdir(parents=True, exist_ok=True)
        logger.info(f"Directory {path} is ready")
    
    return paths

def chunk_document(text, chunk_size=1000, overlap=100):
    """Chunk document text with overlap."""
    chunks = []
    start = 0
    text_length = len(text)
    
    while start < text_length:
        end = min(start + chunk_size, text_length)
        if end < text_length and end - start == chunk_size:
            # Find the last period or newline to make a clean break
            last_period = text.rfind('.', start, end)
            last_newline = text.rfind('\n', start, end)
            break_point = max(last_period, last_newline)
            
            if break_point > start:
                end = break_point + 1  # Include the period or newline
        
        chunk = text[start:end].strip()
        if chunk:  # Only add non-empty chunks
            chunks.append(chunk)
        
        # Move start position for next chunk, considering overlap
        start = end - overlap if end < text_length else text_length
    
    return chunks

def process_pdf(pdf_path, output_dir, has_gpu):
    """Process a single PDF using Docling and create chunks. Also creates individual subfolder."""
    pdf_filename = os.path.basename(pdf_path)
    doc_name = os.path.splitext(pdf_filename)[0]
    
    logger.info(f"Processing {pdf_filename}...")
    
    # Configure Docling
    pipeline_options = PdfPipelineOptions()
    pipeline_options.generate_page_images = True
    
    # Use GPU if available - handle different Docling API versions
    if has_gpu:
        logger.info("Attempting to configure GPU for Docling")
        
        # Try to set device directly on pipeline options first
        try:
            pipeline_options.device = "cuda"
            logger.info("Set pipeline_options.device='cuda'")
        except (AttributeError, ValueError) as e:
            logger.info(f"Could not set pipeline_options.device: {str(e)}")
        
        # Try to enable GPU flag if available
        try:
            pipeline_options.use_gpu = True
            logger.info("Set pipeline_options.use_gpu=True")
        except (AttributeError, ValueError) as e:
            logger.info(f"Could not set pipeline_options.use_gpu: {str(e)}")
            
        # Environment variables are set by setup_gpu_optimizations()
        logger.info("Environment variables for GPU are set globally")
    
    # Initialize Document Converter
    doc_converter = DocumentConverter(
        format_options={
            InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
        }
    )
    
    # Convert the document
    try:
        start_time = time.time()
        result = doc_converter.convert(pdf_path)
        processing_time = time.time() - start_time
        logger.info(f"Processed {pdf_filename} in {processing_time:.2f} seconds")
        
        # Save in multiple formats
        docs_dir = output_dir["docs"]
        chunks_dir = output_dir["chunks"]
        
        # Save document in various formats
        result.document.save_as_json(docs_dir / f"{doc_name}.json", image_mode=ImageRefMode.PLACEHOLDER)
        result.document.save_as_html(docs_dir / f"{doc_name}.html", image_mode=ImageRefMode.EMBEDDED)
        result.document.save_as_markdown(docs_dir / f"{doc_name}.md", image_mode=ImageRefMode.PLACEHOLDER)
        result.document.save_as_markdown(docs_dir / f"{doc_name}.txt", image_mode=ImageRefMode.PLACEHOLDER, strict_text=True)
        
        # Get plain text for chunking
        text_content = result.document.export_to_markdown(strict_text=True)
        
        # Create chunks
        chunks = chunk_document(text_content)
        
        # Save chunks
        with open(chunks_dir / f"{doc_name}_chunks.json", 'w', encoding='utf-8') as f:
            json.dump({
                "document": pdf_filename,
                "total_chunks": len(chunks),
                "chunks": chunks
            }, f, ensure_ascii=False, indent=2)
        
        # Create individual document subfolder
        doc_subdir = docs_dir / doc_name
        doc_subdir.mkdir(exist_ok=True)
        
        # Save document to individual subfolder too
        result.document.save_as_json(doc_subdir / f"{doc_name}.json", image_mode=ImageRefMode.PLACEHOLDER)
        result.document.save_as_html(doc_subdir / f"{doc_name}.html", image_mode=ImageRefMode.EMBEDDED)
        result.document.save_as_markdown(doc_subdir / f"{doc_name}.md", image_mode=ImageRefMode.PLACEHOLDER)
        result.document.save_as_markdown(doc_subdir / f"{doc_name}.txt", image_mode=ImageRefMode.PLACEHOLDER, strict_text=True)
        
        # Save individual chunk files for easier processing
        chunk_dir = chunks_dir / doc_name
        chunk_dir.mkdir(exist_ok=True)
        
        for i, chunk in enumerate(chunks):
            with open(chunk_dir / f"chunk_{i:04d}.txt", 'w', encoding='utf-8') as f:
                f.write(chunk)
        
        return {
            "name": doc_name,
            "path": str(pdf_path),
            "chunks": len(chunks),
            "processing_time": processing_time
        }
        
    except Exception as e:
        logger.error(f"Error processing {pdf_filename}: {str(e)}")
        return None

def main():
    parser = argparse.ArgumentParser(description="Process IBM Redbooks PDFs using Docling")
    parser.add_argument("--data_dir", type=str, default="C:\\Users\\jamie\\OneDrive\\Documents\\Redbooks RAG", 
                        help="Base directory for data storage")
    parser.add_argument("--specific_pdf", type=str, help="Process a specific PDF file only")
    parser.add_argument("--source_dir", type=str, default="C:\\Users\\jamie\\OneDrive\\Documents\\Redbooks PDF Content",
                        help="Source directory containing PDF files")
    args = parser.parse_args()
    
    # Check for GPU
    has_gpu, gpu_info = check_gpu()
    
    # Apply GPU optimizations if available
    if has_gpu:
        setup_gpu_optimizations()
        logger.info(f"GPU optimizations applied for {gpu_info}")
    
    # Setup directories
    directories = setup_directories(args.data_dir)
    
    # Define and load manifest file
    manifest_file = Path(directories["processed"]) / "processing_manifest.json"
    manifest = load_processing_manifest(manifest_file)
    
    # Get list of PDFs to process
    if args.specific_pdf:
        if os.path.exists(args.specific_pdf):
            pdf_files = [args.specific_pdf]
        else:
            logger.error(f"Specified PDF {args.specific_pdf} not found")
            return
    else:
        # Check both the source_dir and the default pdfs directory
        source_dir = Path(args.source_dir)
        pdf_dir = directories["pdfs"]
        
        source_pdfs = [str(f) for f in source_dir.glob("**/*.pdf")] if source_dir.exists() else []
        default_pdfs = [str(f) for f in pdf_dir.glob("*.pdf")]
        
        pdf_files = source_pdfs + default_pdfs
    
    if not pdf_files:
        logger.info("No PDF files found to process")
        return
    
    logger.info(f"Found {len(pdf_files)} PDF files to process")
    
    # Process each PDF, but skip already processed files that haven't changed
    results = []
    skipped = []
    
    for pdf_file in tqdm(pdf_files, desc="Processing PDFs"):
        file_hash = get_file_hash(pdf_file)
        pdf_path = Path(pdf_file)
        
        # Check if file is already processed and hash matches
        if (str(pdf_file) in manifest["processed_files"] and 
            manifest["processed_files"][str(pdf_file)]["hash"] == file_hash and
            manifest["processed_files"][str(pdf_file)]["success"]):
            logger.info(f"Skipping {pdf_path.name} (already processed)")
            skipped.append(pdf_file)
            continue
        
        logger.info(f"Processing {pdf_path.name}")
        
        # Process the PDF
        result = process_pdf(pdf_file, directories, has_gpu)
        
        # Update the manifest
        update_manifest(manifest, manifest_file, pdf_file, file_hash, result is not None)
        
        if result:
            results.append(result)
    
    # Save processing summary
    with open(directories["processed"] / "processing_summary.json", 'w') as f:
        json.dump({
            "processed_date": time.strftime("%Y-%m-%d %H:%M:%S"),
            "total_files": len(results),
            "skipped_files": len(skipped),
            "gpu_used": has_gpu,
            "gpu_info": gpu_info if has_gpu else None,
            "documents": results
        }, f, indent=2)
    
    logger.info(f"Successfully processed {len(results)} out of {len(pdf_files) - len(skipped)} attempted PDFs")
    logger.info(f"Skipped {len(skipped)} files that were already processed")

if __name__ == "__main__":
    main()
