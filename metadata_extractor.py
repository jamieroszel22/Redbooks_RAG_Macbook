import fitz  # PyMuPDF
from pathlib import Path
from typing import Dict, Any, Optional
import logging
from datetime import datetime
import re

logger = logging.getLogger(__name__)

class MetadataExtractor:
    def __init__(self, config: Dict[str, Any]):
        self.config = config

    def extract_metadata(self, pdf_path: Path) -> Dict[str, Any]:
        """Extract metadata from a PDF file."""
        try:
            doc = fitz.open(pdf_path)
            metadata = {
                "title": self._extract_title(doc),
                "author": self._extract_author(doc),
                "date": self._extract_date(doc),
                "abstract": self._extract_abstract(doc),
                "keywords": self._extract_keywords(doc),
                "file_name": pdf_path.name,
                "file_size": pdf_path.stat().st_size,
                "page_count": len(doc),
                "processed_date": datetime.now().isoformat()
            }
            doc.close()
            return metadata
        except Exception as e:
            logger.error(f"Error extracting metadata from {pdf_path}: {e}")
            return {}

    def _extract_title(self, doc: fitz.Document) -> Optional[str]:
        """Extract title from PDF metadata or first page."""
        if self.config.get('extract_title', True):
            # Try to get from PDF metadata first
            title = doc.metadata.get('title')
            if title:
                return title

            # Fallback to first page content
            if len(doc) > 0:
                first_page = doc[0]
                text = first_page.get_text()
                # Look for title-like text (usually first few lines)
                lines = text.split('\n')[:3]
                for line in lines:
                    if len(line.strip()) > 10:  # Avoid very short lines
                        return line.strip()
        return None

    def _extract_author(self, doc: fitz.Document) -> Optional[str]:
        """Extract author from PDF metadata."""
        if self.config.get('extract_author', True):
            return doc.metadata.get('author')
        return None

    def _extract_date(self, doc: fitz.Document) -> Optional[str]:
        """Extract date from PDF metadata or content."""
        if self.config.get('extract_date', True):
            # Try to get from PDF metadata first
            date = doc.metadata.get('creationDate')
            if date:
                return date

            # Fallback to content search
            if len(doc) > 0:
                text = doc[0].get_text()
                # Look for date patterns
                date_patterns = [
                    r'\d{4}-\d{2}-\d{2}',
                    r'\d{2}/\d{2}/\d{4}',
                    r'\d{2}-\d{2}-\d{4}'
                ]
                for pattern in date_patterns:
                    matches = re.findall(pattern, text)
                    if matches:
                        return matches[0]
        return None

    def _extract_abstract(self, doc: fitz.Document) -> Optional[str]:
        """Extract abstract from first few pages."""
        if self.config.get('extract_abstract', True):
            abstract = []
            # Look in first 3 pages for abstract
            for page_num in range(min(3, len(doc))):
                text = doc[page_num].get_text()
                # Look for abstract section
                if "abstract" in text.lower():
                    lines = text.split('\n')
                    for line in lines:
                        if "abstract" in line.lower():
                            continue
                        if line.strip():
                            abstract.append(line.strip())
                            if len(abstract) > 5:  # Limit abstract length
                                break
                    if abstract:
                        break
            return ' '.join(abstract) if abstract else None
        return None

    def _extract_keywords(self, doc: fitz.Document) -> Optional[list]:
        """Extract keywords from PDF metadata or content."""
        if self.config.get('extract_keywords', True):
            # Try to get from PDF metadata first
            keywords = doc.metadata.get('keywords')
            if keywords:
                return keywords.split(',')

            # Fallback to content search
            if len(doc) > 0:
                text = doc[0].get_text()
                # Look for keywords section
                if "keywords" in text.lower():
                    lines = text.split('\n')
                    for line in lines:
                        if "keywords" in line.lower():
                            continue
                        if line.strip():
                            return [k.strip() for k in line.split(',')]
        return None
