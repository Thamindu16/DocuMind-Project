from pathlib import Path
from typing import Literal

from fastapi import FastAPI, File, HTTPException, UploadFile
from pydantic import BaseModel, Field

from src.documind.agent.agent import run_agent_detailed
from src.documind.config import MAX_UPLOAD_MB, UPLOAD_DIR
from src.documind.ingestion.indexer import add_document, delete_document, list_documents
from src.documind.ingestion.loaders import SUPPORTED_EXTENSIONS
from src.documind.rag.pipeline import answer

app = FastAPI(title="DocuMind API")


class Question(BaseModel):
    # Reject empty or very short questions automatically
    question: str = Field(min_length=3)


class Answer(BaseModel):
    answer: str
    sources: list[str]


class ChatTurn(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class ChatRequest(BaseModel):
    message: str = Field(min_length=1)
    history: list[ChatTurn] = []
    # False: answer only from the documents. True: general questions may use the model's own knowledge.
    general_knowledge: bool = False


class UploadResult(BaseModel):
    filename: str
    chunks: int


@app.get("/health")
def health():
    """Simple check that the server is running."""
    return {"status": "ok"}


@app.post("/ask", response_model=Answer)
def ask(body: Question):
    """Answer one question with the plain RAG pipeline (no memory, no tools)."""
    return answer(body.question)


@app.post("/chat", response_model=Answer)
def chat(body: ChatRequest):
    """Conversational endpoint: the agent sees recent history and can use tools."""
    history = [turn.model_dump() for turn in body.history]
    return run_agent_detailed(body.message, history, body.general_knowledge)


@app.post("/upload", response_model=UploadResult)
def upload(file: UploadFile = File(...)):
    """Store an uploaded PDF or text file and add it to the search index."""
    # Keep only the file name so a path such as ../../x cannot escape the upload folder
    name = Path(file.filename or "").name
    if not name:
        raise HTTPException(status_code=400, detail="The file has no name")
    if Path(name).suffix.lower() not in SUPPORTED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Only .pdf and .txt files are supported")

    data = file.file.read()
    if len(data) > MAX_UPLOAD_MB * 1024 * 1024:
        raise HTTPException(status_code=413, detail=f"File is larger than {MAX_UPLOAD_MB} MB")

    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    path = UPLOAD_DIR / name
    path.write_bytes(data)

    try:
        chunk_count = add_document(path)
    except Exception as error:
        path.unlink(missing_ok=True)
        raise HTTPException(status_code=422, detail=f"Could not read the file: {error}")

    if chunk_count == 0:
        path.unlink(missing_ok=True)
        raise HTTPException(
            status_code=422,
            detail="No readable text found. Scanned PDFs (images of text) are not supported.",
        )
    return {"filename": name, "chunks": chunk_count}


@app.get("/documents")
def documents():
    """List every indexed document with its number of chunks."""
    return list_documents()


@app.delete("/documents/{filename}")
def remove_document(filename: str):
    """Remove a document that was uploaded by a user."""
    name = Path(filename).name
    path = UPLOAD_DIR / name
    if not path.exists():
        raise HTTPException(status_code=404, detail="Only uploaded documents can be removed")
    delete_document(name)
    path.unlink()
    return {"removed": name}