from functools import lru_cache

from sentence_transformers import SentenceTransformer

from src.documind.config import EMBEDDING_MODEL


@lru_cache(maxsize=1)
def get_embedder():
    """Load the embedding model once and reuse it."""
    return SentenceTransformer(EMBEDDING_MODEL)


def embed(texts):
    """Convert a string or a list of strings into vectors."""
    return get_embedder().encode(texts).tolist()