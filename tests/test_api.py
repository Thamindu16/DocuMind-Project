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


def test_upload_rejects_unsupported_file_type():
    response = client.post("/upload", files={"file": ("virus.exe", b"abc", "application/octet-stream")})
    assert response.status_code == 400


def test_upload_rejects_file_without_text(monkeypatch, tmp_path):
    monkeypatch.setattr("src.documind.api.main.UPLOAD_DIR", tmp_path)
    monkeypatch.setattr("src.documind.api.main.add_document", lambda path: 0)
    response = client.post("/upload", files={"file": ("empty.txt", b"", "text/plain")})
    assert response.status_code == 422
    assert not (tmp_path / "empty.txt").exists()  # the unusable file is removed


def test_upload_indexes_a_text_file(monkeypatch, tmp_path):
    monkeypatch.setattr("src.documind.api.main.UPLOAD_DIR", tmp_path)
    monkeypatch.setattr("src.documind.api.main.add_document", lambda path: 3)
    response = client.post("/upload", files={"file": ("policy.txt", b"Some policy text", "text/plain")})
    assert response.status_code == 200
    assert response.json() == {"filename": "policy.txt", "chunks": 3}


def test_documents_lists_indexed_files(monkeypatch):
    monkeypatch.setattr(
        "src.documind.api.main.list_documents",
        lambda: [{"source": "hr_policy.txt", "chunks": 4}],
    )
    response = client.get("/documents")
    assert response.json() == [{"source": "hr_policy.txt", "chunks": 4}]


def test_chat_returns_answer_and_sources(monkeypatch):
    monkeypatch.setattr(
        "src.documind.api.main.run_agent_detailed",
        lambda message, history, general_knowledge=False: {"answer": "Hello!", "sources": []},
    )
    response = client.post("/chat", json={"message": "hi"})
    assert response.status_code == 200
    assert response.json() == {"answer": "Hello!", "sources": []}


def test_chat_passes_history_to_agent(monkeypatch):
    captured = {}

    def fake_agent(message, history, general_knowledge=False):
        captured["message"] = message
        captured["history"] = history
        return {"answer": "ok", "sources": []}

    monkeypatch.setattr("src.documind.api.main.run_agent_detailed", fake_agent)
    history = [
        {"role": "user", "content": "How many sick days?"},
        {"role": "assistant", "content": "7 days."},
    ]
    response = client.post("/chat", json={"message": "and annual leave?", "history": history})
    assert response.status_code == 200
    assert captured["message"] == "and annual leave?"
    assert captured["history"] == history


def test_chat_passes_general_knowledge_flag(monkeypatch):
    captured = {}

    def fake_agent(message, history, general_knowledge=False):
        captured["flag"] = general_knowledge
        return {"answer": "ok", "sources": []}

    monkeypatch.setattr("src.documind.api.main.run_agent_detailed", fake_agent)
    client.post("/chat", json={"message": "what is RAG?", "general_knowledge": True})
    assert captured["flag"] is True


def test_chat_rejects_empty_message():
    response = client.post("/chat", json={"message": ""})
    assert response.status_code == 422