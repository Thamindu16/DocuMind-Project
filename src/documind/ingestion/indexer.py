from pathlib import Path

import chromadb

from src.documind.config import COLLECTION_NAME, RAW_DATA_DIR, UPLOAD_DIR, VECTORSTORE_DIR
from src.documind.embeddings.embedder import embed
from src.documind.ingestion.chunking import chunk_by_paragraph
from src.documind.ingestion.loaders import SUPPORTED_EXTENSIONS, extract_text


def _client():
    return chromadb.PersistentClient(path=str(VECTORSTORE_DIR))


def _collection():
    return _client().get_or_create_collection(
        name=COLLECTION_NAME, metadata={"hnsw:space": "cosine"}
    )


def _chunks_for(path):
    """Return ids, texts and metadata for every chunk of one file."""
    texts = chunk_by_paragraph(extract_text(path))
    ids = [f"{path.parent.name}/{path.name}-{i}" for i in range(len(texts))]
    metadatas = [{"source": path.name} for _ in texts]
    return ids, texts, metadatas


def add_document(path):
    """Index one file without touching the others. Returns the number of chunks stored."""
    path = Path(path)
    ids, texts, metadatas = _chunks_for(path)
    if not texts:
        return 0
    collection = _collection()
    # Replace any older version of a file with the same name
    collection.delete(where={"source": path.name})
    collection.add(ids=ids, documents=texts, embeddings=embed(texts), metadatas=metadatas)
    return len(texts)


def delete_document(filename):
    """Remove every chunk that came from the given file."""
    _collection().delete(where={"source": filename})


def list_documents():
    """Return each indexed file with its number of chunks."""
    metadatas = _collection().get(include=["metadatas"])["metadatas"]
    counts = {}
    for meta in metadatas:
        counts[meta["source"]] = counts.get(meta["source"], 0) + 1
    return [{"source": name, "chunks": count} for name, count in sorted(counts.items())]


def build_index():
    """Rebuild the whole index from the project documents and all uploads."""
    files = []
    for folder in (RAW_DATA_DIR, UPLOAD_DIR):
        if folder.exists():
            files += [p for p in sorted(folder.iterdir()) if p.suffix.lower() in SUPPORTED_EXTENSIONS]

    client = _client()
    # Start from a clean collection so old chunks never remain
    try:
        client.delete_collection(COLLECTION_NAME)
    except Exception:
        pass
    collection = client.create_collection(name=COLLECTION_NAME, metadata={"hnsw:space": "cosine"})

    total = 0
    for path in files:
        ids, texts, metadatas = _chunks_for(path)
        if texts:
            collection.add(ids=ids, documents=texts, embeddings=embed(texts), metadatas=metadatas)
            total += len(texts)
    print(f"Indexed {total} chunks from {len(files)} files")


if __name__ == "__main__":
    build_index()