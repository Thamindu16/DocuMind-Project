import os
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_chroma import Chroma

from src.config import DOCS_DIR, CHROMA_DB_DIR, EMBEDDING_MODEL_NAME, CHUNK_SIZE, CHUNK_OVERLAP

def ingest_documents():
    print("1. Loading documents from directory...")
    # Load all .txt files from the docs directory
    loader = DirectoryLoader(DOCS_DIR, glob="**/*.txt", loader_cls=TextLoader)
    documents = loader.load()
    
    if not documents:
        print("No documents found in data/docs/. Please add some .txt files.")
        return

    print(f"Loaded {len(documents)} documents.")

    print("2. Splitting documents into chunks...")
    # Split documents into smaller chunks so the LLM can process them
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP
    )
    chunks = text_splitter.split_documents(documents)
    print(f"Created {len(chunks)} chunks.")

    print("3. Creating embeddings and storing in ChromaDB...")
    # Initialize the free local embedding model
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)

    # Delete existing database to prevent duplicate data during testing
    if os.path.exists(CHROMA_DB_DIR):
        import shutil
        shutil.rmtree(CHROMA_DB_DIR)

    # Create new vector database and store the chunks
    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=CHROMA_DB_DIR
    )
    
    print("Ingestion complete! Data is safely stored in ChromaDB.")

if __name__ == "__main__":
    ingest_documents()