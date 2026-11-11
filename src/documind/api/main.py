from fastapi import FastAPI
from pydantic import BaseModel, Field

from src.documind.rag.pipeline import answer

app = FastAPI(title="DocuMind API")


class Question(BaseModel):
    # Reject empty or very short questions automatically
    question: str = Field(min_length=3)


class Answer(BaseModel):
    answer: str
    sources: list[str]


@app.get("/health")
def health():
    """Simple check that the server is running."""
    return {"status": "ok"}


@app.post("/ask", response_model=Answer)
def ask(body: Question):
    """Answer a question using the RAG pipeline."""
    return answer(body.question)