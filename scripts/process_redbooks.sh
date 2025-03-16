#!/bin/bash
# Process Redbooks PDFs with Docling

echo "Starting Redbook processing..."
python /app/redbook-processor.py /data/pdfs /data/processed_redbooks/docs
echo "Processing complete!"
