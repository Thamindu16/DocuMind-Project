import glob
import os

import chromadb
from sentence_transformers import SentenceTransformer

CHUNK_SIZE = 300      # characters per chunk
CHUNK_OVERLAP = 50    # characters shared between neighbouring chunks


def chunk_text(text, size, overlap):
    """Split text into fixed-size pieces that overlap slightly."""
    chunks = []
    start = 0
    while start < len(text):
        chunks.append(text[start:start + size])
        start += size - overlap
    return chunks


model = SentenceTransformer("all-MiniLM-L6-v2")

# A persistent vector database stored on disk
client = chromadb.PersistentClient(path="data/vectorstore")
collection = client.get_or_create_collection(
    name="documind",
    metadata={"hnsw:space": "cosine"},
)

# 1. Load every .txt file and split it into chunks
ids, texts, metadatas = [], [], []
for path in glob.glob("data/raw/*.txt"):
    filename = os.path.basename(path)
    with open(path, encoding="utf-8") as file:
        content = file.read()
    for index, chunk in enumerate(chunk_text(content, CHUNK_SIZE, CHUNK_OVERLAP)):
        ids.append(f"{filename}-{index}")
        texts.append(chunk)
        metadatas.append({"source": filename})

# 2. Turn chunks into vectors and store them
embeddings = model.encode(texts).tolist()
collection.upsert(ids=ids, documents=texts, embeddings=embeddings, metadatas=metadatas)
print(f"Stored {len(texts)} chunks")

# 3. Ask a question and fetch the 3 closest chunks
query = "How many days off do I get each year?"
results = collection.query(
    query_embeddings=model.encode(query).tolist(),
    n_results=3,
)

for doc, meta, distance in zip(
    results["documents"][0], results["metadatas"][0], results["distances"][0]
):
    print(f"\n[{meta['source']}] distance={distance:.3f}")
    print(doc)