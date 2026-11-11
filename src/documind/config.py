from pathlib import Path

# Project root is two levels above this file (src/documind/config.py)
BASE_DIR = Path(__file__).resolve().parents[2]
RAW_DATA_DIR = BASE_DIR / "data" / "raw"
VECTORSTORE_DIR = BASE_DIR / "data" / "vectorstore"

COLLECTION_NAME = "documind"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
LLM_MODEL = "openai/gpt-oss-120b"
TOP_K = 3