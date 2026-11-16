from src.documind.ingestion.indexer import list_documents
from src.documind.retrieval.retriever import retrieve

print("Indexed documents:")
for doc in list_documents():
    print(f"  {doc['source']}: {doc['chunks']} chunks")

query = "Can I accept a gift from a supplier?"
print(f"\nTop 8 chunks for: {query}")
for rank, chunk in enumerate(retrieve(query, k=8), start=1):
    print(f"{rank}. distance={chunk['distance']:.3f} [{chunk['source']}] {chunk['text'][:90]}")