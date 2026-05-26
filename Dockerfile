# Rasaveda — self-contained deployment image
# Bundles the Streamlit app + Ollama in one container (no HuggingFace required).
#
# Build:  docker build -t rasaveda .
# Run:    docker run -p 8501:8501 rasaveda
#
# For cloud: push to Railway, Render, or Fly.io (needs at least 4GB RAM for qwen2.5:7b)
# For low-RAM cloud (free tier): change BASE_MODEL to llama3.2:1b or qwen2.5:0.5b

ARG BASE_MODEL=qwen2.5:7b

FROM ollama/ollama:latest AS ollama-base

# Install Python + app dependencies
RUN apt-get update && apt-get install -y \
    python3 python3-pip curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

COPY . .

# Entrypoint script: start Ollama, pull/create model, then launch Streamlit
COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

EXPOSE 8501

ENTRYPOINT ["/docker-entrypoint.sh"]
