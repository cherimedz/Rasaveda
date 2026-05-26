"""
Ollama LLM client — all inference runs locally via Ollama.

Set OLLAMA_MODEL and OLLAMA_BASE_URL in .env to control which model is used.
Default model: rasaveda (custom Modelfile) or qwen2.5:7b as fallback.
"""

import ollama

from thyme_machine.config import settings


def chat_complete(messages: list[dict], max_tokens: int, temperature: float) -> str:
    """Send a chat request to the local Ollama server and return the response text."""
    client = ollama.Client(host=settings.ollama_base_url)
    response = client.chat(
        model=settings.ollama_model,
        messages=messages,
        options={"num_predict": max_tokens, "temperature": temperature},
    )
    return response.message.content
