#!/bin/bash
# Run the interactive RAG with Ollama

echo "Starting interactive RAG system..."
python /app/ollama-rag-integration.py --model ${OLLAMA_MODEL:-granite3.2:8b-instruct-fp16} --chunks_dir /data/processed_redbooks/chunks
