import os

from langchain_ollama import ChatOllama


def get_llm():
    """Crée le modèle Ollama configuré pour des réponses reproductibles."""
    model = os.getenv("OLLAMA_MODEL", "qwen2.5-coder:7b")
    context_length = int(os.getenv("OLLAMA_NUM_CTX", "8192"))

    return ChatOllama(
        model=model,
        temperature=0,
        num_ctx=context_length,
    )