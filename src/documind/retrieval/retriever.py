import chromadb

from src.documind.config import COLLECTION_NAME, TOP_K, VECTORSTORE_DIR
from src.documind.embeddings.embedder import embed


def retrieve(question, k=TOP_K):
    """Return the k chunks closest in meaning to the question."""
    client = chromadb.PersistentClient(path=str(VECTORSTORE_DIR))
    collection = client.get_collection(COLLECTION_NAME)
    results = collection.query(query_embeddings=[embed(question)], n_results=k)
    return [
        {"text": text, "source": meta["source"], "distance": distance}
        for text, meta, distance in zip(
            results["documents"][0], results["metadatas"][0], results["distances"][0]
        )
    ]