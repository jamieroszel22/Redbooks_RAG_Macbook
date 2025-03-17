import logging
from pathlib import Path
from typing import List, Dict, Any
import json
import fitz
from concurrent.futures import ThreadPoolExecutor
import hashlib
from datetime import datetime

from config_loader import ConfigLoader
from metadata_extractor import MetadataExtractor

logger = logging.getLogger(__name__)

class DocumentProcessor:
    def __init__(self, config_path: str = "config.yaml"):
        self.config_loader = ConfigLoader(config_path)
        self.config = self.config_loader.config
        self.metadata_extractor = MetadataExtractor(self.config['metadata'])
        self.processed_files = set()

    def process_documents(self, incremental: bool = True) -> None:
        """Process all PDF documents in the configured directory."""
        pdf_dir = self.config_loader.get_path('pdf_dir')
        processed_dir = self.config_loader.get_path('processed_dir')
        temp_dir = self.config_loader.get_path('temp_dir')

        # Create necessary directories
        for dir_path in [processed_dir, temp_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)

        # Get list of PDF files
        pdf_files = list(pdf_dir.glob("*.pdf"))
        if not pdf_files:
            logger.warning(f"No PDF files found in {pdf_dir}")
            return

        # Load processed files record if incremental processing
        if incremental:
            self._load_processed_files(processed_dir)

        # Process files in parallel if configured
        if self.config['processing']['parallel_processing']:
            with ThreadPoolExecutor(max_workers=self.config['processing']['max_workers']) as executor:
                futures = [executor.submit(self._process_single_document, pdf_file) for pdf_file in pdf_files]
                for future in futures:
                    future.result()
        else:
            for pdf_file in pdf_files:
                self._process_single_document(pdf_file)

        # Save processed files record
        if incremental:
            self._save_processed_files(processed_dir)

    def _process_single_document(self, pdf_path: Path) -> None:
        """Process a single PDF document."""
        try:
            # Check if file needs processing
            if self._should_skip_file(pdf_path):
                logger.info(f"Skipping already processed file: {pdf_path}")
                return

            # Extract metadata
            metadata = self.metadata_extractor.extract_metadata(pdf_path)
            if not metadata:
                logger.error(f"Failed to extract metadata from {pdf_path}")
                return

            # Create document directory
            doc_dir = self.config_loader.get_path('processed_dir') / pdf_path.stem
            doc_dir.mkdir(exist_ok=True)

            # Save metadata
            metadata_file = doc_dir / "metadata.json"
            with open(metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2)

            # Process document content
            self._process_content(pdf_path, doc_dir, metadata)

            # Mark as processed
            self.processed_files.add(pdf_path.name)
            logger.info(f"Successfully processed {pdf_path}")

        except Exception as e:
            logger.error(f"Error processing {pdf_path}: {e}")

    def _process_content(self, pdf_path: Path, doc_dir: Path, metadata: Dict[str, Any]) -> None:
        """Process document content into chunks."""
        doc = fitz.open(pdf_path)
        chunks_dir = doc_dir / "chunks"
        chunks_dir.mkdir(exist_ok=True)

        pdf_config = self.config['pdf_processing']
        chunk_size = pdf_config['chunk_size']
        chunk_overlap = pdf_config['chunk_overlap']
        min_chunk_size = pdf_config['min_chunk_size']
        max_chunk_size = pdf_config['max_chunk_size']

        current_chunk = []
        current_size = 0
        chunk_number = 0

        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text()
            words = text.split()

            for word in words:
                word_size = len(word) + 1  # +1 for space
                if current_size + word_size > chunk_size:
                    if current_size >= min_chunk_size:
                        self._save_chunk(chunks_dir, chunk_number, current_chunk, metadata)
                        chunk_number += 1
                    current_chunk = [word]
                    current_size = word_size
                else:
                    current_chunk.append(word)
                    current_size += word_size

        # Save the last chunk if it meets minimum size
        if current_size >= min_chunk_size:
            self._save_chunk(chunks_dir, chunk_number, current_chunk, metadata)

        doc.close()

    def _save_chunk(self, chunks_dir: Path, chunk_number: int, words: List[str], metadata: Dict[str, Any]) -> None:
        """Save a chunk of text with its metadata."""
        content = ' '.join(words)
        chunk_data = {
            "content": content,
            "metadata": {
                **metadata,
                "chunk_number": chunk_number,
                "word_count": len(words),
                "processed_date": datetime.now().isoformat()
            }
        }

        chunk_file = chunks_dir / f"chunk_{chunk_number:04d}.json"
        with open(chunk_file, 'w') as f:
            json.dump(chunk_data, f, indent=2)

    def _should_skip_file(self, pdf_path: Path) -> bool:
        """Check if a file should be skipped based on incremental processing settings."""
        return pdf_path.name in self.processed_files

    def _load_processed_files(self, processed_dir: Path) -> None:
        """Load the record of processed files."""
        record_file = processed_dir / "processed_files.json"
        if record_file.exists():
            with open(record_file, 'r') as f:
                self.processed_files = set(json.load(f))

    def _save_processed_files(self, processed_dir: Path) -> None:
        """Save the record of processed files."""
        record_file = processed_dir / "processed_files.json"
        with open(record_file, 'w') as f:
            json.dump(list(self.processed_files), f, indent=2)

def main():
    # Set up logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    # Process documents
    processor = DocumentProcessor()
    processor.process_documents(incremental=True)

if __name__ == "__main__":
    main()
