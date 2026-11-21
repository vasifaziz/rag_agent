import chromadb
import os

DB_PATH = os.path.join(
    os.environ["LOCALAPPDATA"],
    "RAG",
    "chroma_db"
)

os.makedirs(DB_PATH, exist_ok=True)

client = chromadb.PersistentClient(
    path=DB_PATH
)

print("ChromaDB initialized successfully!")

collection = (
    client.get_or_create_collection(
        name="documents"
    )
)


def add_chunks(chunks):

    documents = []
    embeddings = []
    ids = []
    metadatas = []

    for chunk in chunks:

        documents.append(
            chunk["text"]
        )

        embeddings.append(
            chunk["embedding"]
        )

        ids.append(
            f'{chunk["source"]}_'
            f'{chunk["chunk_id"]}'
        )

        metadatas.append({
            "source": chunk["source"],
            "chunk_id": chunk["chunk_id"]
        })

    collection.upsert(
        ids=ids,
        documents=documents,
        embeddings=embeddings,
        metadatas=metadatas
    )


def search(
    query_embedding,
    top_k=5
):

    return collection.query(
        query_embeddings=[
            query_embedding
        ],
        n_results=top_k
    )
