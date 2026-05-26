#!/bin/bash
# Start Ollama server in background, pull/create the Rasaveda model, then run the app.

set -e

echo "Starting Ollama server..."
ollama serve &
OLLAMA_PID=$!

# Wait for Ollama to be ready
echo "Waiting for Ollama to be ready..."
until curl -s http://localhost:11434/api/version > /dev/null 2>&1; do
    sleep 1
done
echo "Ollama is ready."

# Create the custom Rasaveda model from the Modelfile
echo "Creating Rasaveda model..."
ollama create rasaveda -f /app/Modelfile

echo "Rasaveda model ready."

# Ingest recipes into ChromaDB if not already done
if [ ! -d "/app/chroma_db" ]; then
    echo "Ingesting recipes into ChromaDB..."
    python3 /app/ingest.py
fi

echo "Starting Streamlit app..."
exec streamlit run /app/app.py \
    --server.port=8501 \
    --server.address=0.0.0.0 \
    --server.headless=true
