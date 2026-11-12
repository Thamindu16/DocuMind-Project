from fastapi.testclient import TestClient

from src.documind.api.main import app

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_rejects_too_short_question():
    response = client.post("/ask", json={"question": "hi"})
    assert response.status_code == 422


def test_rejects_missing_question():
    response = client.post("/ask", json={})
    assert response.status_code == 422


def test_ask_returns_answer_and_sources(monkeypatch):
    """Replace the RAG pipeline with a fake so no LLM call is made."""
    monkeypatch.setattr(
        "src.documind.api.main.answer",
        lambda question: {"answer": "14 days", "sources": ["hr_policy.txt"]},
    )
    response = client.post("/ask", json={"question": "How many leave days?"})
    assert response.status_code == 200
    assert response.json() == {"answer": "14 days", "sources": ["hr_policy.txt"]}