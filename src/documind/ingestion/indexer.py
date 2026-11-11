import chromadb

from src.documind.config import COLLECTION_NAME, RAW_DATA_DIR, VECTORSTORE_DIR
from src.documind.embeddings.embedder import embed
from src.documind.ingestion.chunking import chunk_by_paragraph


def build_index():
    """Read all .txt files, chunk them, embed them and store them in ChromaDB."""
    ids, texts, metadatas = [], [], []
    for path in sorted(RAW_DATA_DIR.glob("*.txt")):
        content = path.read_text(encoding="utf-8")
        for index, chunk in enumerate(chunk_by_paragraph(content)):
            ids.append(f"{path.name}-{index}")
            texts.append(chunk)
            metadatas.append({"source": path.name})

    client = chromadb.PersistentClient(path=str(VECTORSTORE_DIR))
    # Start from a clean collection so old chunks never remain
    try:
        client.delete_collection(COLLECTION_NAME)
    except Exception:
        pass
    collection = client.create_collection(
        name=COLLECTION_NAME, metadata={"hnsw:space": "cosine"}
    )
    collection.add(ids=ids, documents=texts, embeddings=embed(texts), metadatas=metadatas)
    print(f"Indexed {len(texts)} chunks")


if __name__ == "__main__":
    build_index()