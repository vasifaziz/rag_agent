# Working Process Knowledge Assistant

A local RAG demo that answers questions from the SMB and Enterprise working-process documents. It reads Word `.docx` files from `Documents`, keeps their headings and tables in context, retrieves relevant sections, reranks them, and shows the sources used for each answer.

## Run locally

Requirements: Python 3.10+, Ollama, and the Python packages in `requirements.txt`.

```powershell
python -m pip install -r requirements.txt
ollama pull nomic-embed-text
ollama pull qwen3:4b
python main.py
```

The first run indexes the documents. Unchanged documents reuse their existing local Chroma index. Put additional `.docx` files in `Documents` to include them in the next run.

The default Ollama models can be overridden with `RAG_BASE_URL`, `RAG_API_KEY`, `RAG_CHAT_MODEL`, and `RAG_EMBEDDING_MODEL`. `RAG_TIMEOUT_SECONDS` sets the model request timeout (120 seconds by default).

Try questions such as:

- How does the SMB process identify content opportunities?
- How does the Enterprise process handle approvals and failures?
- What business problems do the two processes address?
