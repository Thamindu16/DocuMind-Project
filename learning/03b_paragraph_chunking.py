import glob
import os

import chromadb
from sentence_transformers import SentenceTransformer


def chunk_by_paragraph(text, min_length=40):
    """Split text on blank lines; each paragraph becomes one chunk."""
    paragraphs = [p.strip() for p in text.split("\n\n")]
    # Drop very short pieces such as document titles
    return [p for p in paragraphs if len(p) >= min_length]


model = SentenceTransformer("all-MiniLM-L6-v2")
client = chromadb.PersistentClient(path="data/vectorstore")

# Remove the old collection so chunks from the previous strategy do not remain
try:
    client.delete_collection("documind")
except Exception:
    pass

collection = client.create_collection(
    name="documind",
    metadata={"hnsw:space": "cosine"},
)

# 1. Load every .txt file and split it into paragraph chunks
ids, texts, metadatas = [], [], []
for path in glob.glob("data/raw/*.txt"):
    filename = os.path.basename(path)
    with open(path, encoding="utf-8") as file:
        content = file.read()
    for index, chunk in enumerate(chunk_by_paragraph(content)):
        ids.append(f"{filename}-{index}")
        texts.append(chunk)
        metadatas.append({"source": filename})

# 2. Turn chunks into vectors and store them
embeddings = model.encode(texts).tolist()
collection.add(ids=ids, documents=texts, embeddings=embeddings, metadatas=metadatas)
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