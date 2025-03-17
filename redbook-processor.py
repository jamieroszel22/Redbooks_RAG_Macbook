import argparse
import logging
import os
import time
import sys
import shutil
from pathlib import Path
import json
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
    """Process a single PDF using Docling and create chunks."""
    pdf_filename = os.path.basename(pdf_path)
    doc_name = os.path.splitext(pdf_filename)[0]
    
    logger.info(f"Processing {pdf_filename}...")
    
    # Configure Docling
    pipeline_options = PdfPipelineOptions()
    pipeline_options.generate_page_images = True
    
    # Use GPU if available - handle different Docling API versions
    if has_gpu:
        logger.info("Attempting to configure GPU for Docling")
        gpu_configured = False
        
        # The specific API for GPU configuration varies across Docling versions
        # We'll try several possible methods and gracefully handle failures
        
        # Method 1: Try checking the available attributes of PdfPipelineOptions
        available_attrs = dir(pipeline_options)
        gpu_related_attrs = [attr for attr in available_attrs if any(term in attr.lower() for term in ['gpu', 'cuda', 'device'])]
        
        if gpu_related_attrs:
            logger.info(f"Found potential GPU-related attributes: {gpu_related_attrs}")
            for attr in gpu_related_attrs:
                try:
                    # Try to enable the attribute if it looks like a boolean flag
                    if attr.lower().startswith(('use_', 'enable_', 'has_')):
                        setattr(pipeline_options, attr, True)
                        logger.info(f"Set {attr}=True on pipeline_options")
                        gpu_configured = True
                    # Try to set device if it looks like a device property
                    elif any(term in attr.lower() for term in ['device', 'gpu', 'cuda']):
                        setattr(pipeline_options, attr, "cuda")
                        logger.info(f"Set {attr}='cuda' on pipeline_options")
                        gpu_configured = True
                except (AttributeError, ValueError, TypeError) as e:
                    logger.info(f"Could not set {attr}: {str(e)}")
        
        # Method 2: Try to modify settings directly
        if not gpu_configured:
            try:
                # Check if settings has gpu or device related attributes
                settings_attrs = dir(settings)
                gpu_settings_attrs = [attr for attr in settings_attrs if any(term in attr.lower() for term in ['gpu', 'cuda', 'device'])]
                
                if gpu_settings_attrs:
                    logger.info(f"Found potential GPU settings: {gpu_settings_attrs}")
                    for attr in gpu_settings_attrs:
                        try:
                            # For dict-like attributes (e.g. settings.gpu might be a dict/object)
                            sub_obj = getattr(settings, attr)
                            sub_attrs = dir(sub_obj)
                            
                            for sub_attr in sub_attrs:
                                if any(term in sub_attr.lower() for term in ['enable', 'use', 'active']):
                                    setattr(sub_obj, sub_attr, True)
                                    logger.info(f"Set settings.{attr}.{sub_attr}=True")
                                    gpu_configured = True
                                    break
                        except (AttributeError, TypeError):
                            # If not a dict-like object, try setting directly
                            try:
                                setattr(settings, attr, "cuda")
                                logger.info(f"Set settings.{attr}='cuda'")
                                gpu_configured = True
                            except (AttributeError, ValueError, TypeError) as e:
                                logger.info(f"Could not set settings.{attr}: {str(e)}")
            except Exception as e:
                logger.info(f"Error trying to configure GPU via settings: {str(e)}")
        
        # Method 3: Set environment variables as a last resort
        if not gpu_configured:
            logger.info("Setting environment variables for GPU usage")
            os.environ["DOCLING_USE_GPU"] = "1"
            os.environ["CUDA_VISIBLE_DEVICES"] = "0"
        
        # Status update
        if gpu_configured:
            logger.info("Successfully configured Docling to use GPU")
        else:
            logger.info("Couldn't directly configure GPU. Environment variables set. Docling will use CPU if GPU not automatically detected.")
    
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
    args = parser.parse_args()
    
    # Check for GPU
    has_gpu, gpu_info = check_gpu()
    
    # Setup directories
    directories = setup_directories(args.data_dir)
    
    # Get list of PDFs to process
    if args.specific_pdf:
        if os.path.exists(args.specific_pdf):
            pdf_files = [args.specific_pdf]
        else:
            logger.error(f"Specified PDF {args.specific_pdf} not found")
            return
    else:
        pdf_dir = directories["pdfs"]
        pdf_files = [str(f) for f in pdf_dir.glob("*.pdf")]
    
    if not pdf_files:
        logger.info("No PDF files found to process")
        return
    
    logger.info(f"Found {len(pdf_files)} PDF files to process")
    
    # Process each PDF
    results = []
    for pdf_file in tqdm(pdf_files, desc="Processing PDFs"):
        result = process_pdf(pdf_file, directories, has_gpu)
        if result:
            results.append(result)
    
    # Save processing summary
    with open(directories["processed"] / "processing_summary.json", 'w') as f:
        json.dump({
            "processed_date": time.strftime("%Y-%m-%d %H:%M:%S"),
            "total_files": len(results),
            "gpu_used": has_gpu,
            "gpu_info": gpu_info if has_gpu else None,
            "documents": results
        }, f, indent=2)
    
    logger.info(f"Successfully processed {len(results)} out of {len(pdf_files)} PDFs")

if __name__ == "__main__":
    main()
