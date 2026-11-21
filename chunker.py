def create_chunks(sections, source, chunk_size=280, overlap=45):
    if chunk_size <= 0 or overlap < 0 or overlap >= chunk_size:
        raise ValueError("chunk_size must be positive and greater than overlap")

    chunks = []
    for section in sections:
        words = section["text"].split()
        step = chunk_size - overlap
        start = 0

        while start < len(words):
            body = " ".join(words[start:start + chunk_size])
            title = section.get("document_title", source)
            heading = section.get("section", title)
            chunks.append({
                "text": f"{title} - {heading}\n{body}",
                "source": source,
                "section": heading,
                "chunk_id": len(chunks),
            })
            start += step

    return chunks
