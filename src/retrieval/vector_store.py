from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_chroma import Chroma

from src.config import CHROMA_DB_DIR, EMBEDDING_MODEL_NAME

def get_retriever():
    print("Loading existing vector database...")
    # Load the same embedding model used during ingestion
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)
    
    # Connect to the existing ChromaDB directory
    vectorstore = Chroma(
        persist_directory=CHROMA_DB_DIR, 
        embedding_function=embeddings
    )
    
    # Return a retriever that fetches the top 3 most relevant chunks
    retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
    return retriever

if __name__ == "__main__":
    # Test script to check if retrieval works
    retriever = get_retriever()
    query = "What is the policy for remote work?"
    print(f"\nTesting retrieval for query: '{query}'")
    
    docs = retriever.invoke(query)
    print(f"\nFound {len(docs)} relevant chunks:")
    for i, doc in enumerate(docs):
        print(f"\n--- Chunk {i+1} ---")
        print(doc.page_content)