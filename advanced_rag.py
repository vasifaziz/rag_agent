import hashlib
from pathlib import Path

from chunker import create_chunks
from document_loader import load_docx
from embeddings import create_embedding, embed_chunks
from chroma_store import replace_source, search as chroma_search, source_is_current
from retriever import keyword_score
from reranker import rerank


def build_rag(document_paths):
    paths = [Path(path) for path in document_paths]
    if not paths:
        raise ValueError("No .docx documents were provided")

    indexed = 0
    cached = 0
    total_chunks = 0

    for path in paths:
        sections = load_docx(path)
        source = path.name
        document_hash = hashlib.sha256(path.read_bytes()).hexdigest()
        chunks = create_chunks(sections, source=source)
        total_chunks += len(chunks)

        if source_is_current(source, document_hash, len(chunks)):
            cached += 1
            continue

        for chunk in chunks:
            chunk["document_hash"] = document_hash
        embedded_chunks = embed_chunks(chunks)
        replace_source(source, embedded_chunks)
        indexed += 1

    return {
        "sources": [path.name for path in paths],
        "indexed": indexed,
        "cached": cached,
        "chunks": total_chunks,
    }


def retrieve(query, top_k=4, sources=None):
    if not query.strip():
        return []

    query_embedding = create_embedding(query)
    semantic_results = chroma_search(
        query_embedding,
        top_k=max(top_k * 3, 12),
        sources=sources,
    )

    candidates = []
    documents = semantic_results["documents"][0] or []
    metadatas = semantic_results["metadatas"][0] or []
    distances = semantic_results["distances"][0] or []

    for text, metadata, distance in zip(documents, metadatas, distances):
        semantic = 1 / (1 + distance)
        keyword = keyword_score(query, text)
        candidates.append({
            "text": text,
            "source": metadata["source"],
            "chunk_id": metadata["chunk_id"],
            "section": metadata["section"],
            "semantic_score": semantic,
            "keyword_score": keyword,
            "combined_score": 0.7 * semantic + 0.3 * keyword,
        })

    candidates.sort(key=lambda item: item["combined_score"], reverse=True)
    return rerank(query, candidates[:max(top_k, 4)], top_k=top_k)
