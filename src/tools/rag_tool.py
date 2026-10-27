from langchain_core.tools import tool
from src.retrieval.vector_store import get_retriever

# Load the retriever once
retriever = get_retriever()

@tool
def search_internal_docs(query: str) -> str:
    """Useful for searching internal company documents like HR policies, 
    IT security policies, and Customer Support SOPs. 
    Input should be a specific question."""
    # Get the top 3 relevant chunks from ChromaDB
    docs = retriever.invoke(query)
    
    # Combine the text from the chunks
    combined_text = "\n\n".join([doc.page_content for doc in docs])
    return combined_text