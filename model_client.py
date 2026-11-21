import os

from openai import OpenAI


client = OpenAI(
    base_url=os.getenv("RAG_BASE_URL", "http://localhost:11434/v1"),
    api_key=os.getenv("RAG_API_KEY", "ollama"),
    timeout=float(os.getenv("RAG_TIMEOUT_SECONDS", "120")),
    max_retries=0,
)

CHAT_MODEL = os.getenv("RAG_CHAT_MODEL", "qwen3:4b")
EMBEDDING_MODEL = os.getenv("RAG_EMBEDDING_MODEL", "nomic-embed-text")
