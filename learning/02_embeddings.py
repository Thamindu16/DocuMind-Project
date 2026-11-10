from sentence_transformers import SentenceTransformer, util

# Load a small pre-trained embedding model (downloads once, then cached)
model = SentenceTransformer("all-MiniLM-L6-v2")

# A question and three candidate sentences
query = "How many days off do I get each year?"
documents = [
    "Staff are entitled to 14 days of paid vacation annually.",
    "The office cafeteria serves lunch from noon to 2 PM.",
    "Employees must change their passwords every 90 days.",
]

# Convert text into vectors
query_vector = model.encode(query)
document_vectors = model.encode(documents)

# Compare the query vector with every document vector
scores = util.cos_sim(query_vector, document_vectors)[0]

# Print documents from most to least similar
ranked = sorted(zip(documents, scores), key=lambda pair: pair[1], reverse=True)
for document, score in ranked:
    print(f"{score:.3f}  {document}")

# Show how many numbers make up one vector
print("Vector size:", len(query_vector))