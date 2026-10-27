import os
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# Define absolute paths for the project
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS_DIR = os.path.join(BASE_DIR, "data", "docs")
CHROMA_DB_DIR = os.path.join(BASE_DIR, "data", "chroma_db")

# Fetch API Keys from environment variables
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Model Configurations
# We will use Groq's Llama 3 model for fast and free generation
LLM_MODEL_NAME = "llama-3.1-70b-versatile" 
EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2" # Free local embedding model

# Data Processing Settings
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50