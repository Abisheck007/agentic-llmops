from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.api import routes

client = TestClient(app)


def test_query_endpoint_returns_success(monkeypatch):
    async def fake_run_agent(question, session_id=None):
        return {
            "answer": "Agentic RAG combines retrieval with agent orchestration. [1]",
            "sources": [
                {
                    "document_id": "rag-003",
                    "title": "Agentic RAG",
                    "content": (
                        "Agentic RAG adds an orchestration layer "
                        "to retrieval-augmented generation."
                    ),
                    "page_number": 1,
                    "source_url": "https://example.com/agentic-rag",
                }
            ],
            "steps": [
                "Retrieved 1 document(s) from Azure AI Search.",
                "Retrieved context appears relevant to the question.",
                "Generated an answer using the retrieved context.",
            ],
        }

    monkeypatch.setattr(routes, "run_agent", fake_run_agent)

    response = client.post(
        "/api/v1/query",
        json={
            "question": "What is Agentic RAG?",
            "session_id": "test-session-001",
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["status"] == "completed"
    assert "Agentic RAG" in body["answer"]
    assert body["session_id"] == "test-session-001"
    assert len(body["sources"]) == 1
    assert len(body["agent_steps"]) == 3


def test_query_endpoint_rejects_empty_question():
    response = client.post(
        "/api/v1/query",
        json={
            "question": "",
            "session_id": "test-session-002",
        },
    )

    assert response.status_code == 422


def test_query_endpoint_rejects_missing_question():
    response = client.post(
        "/api/v1/query",
        json={
            "session_id": "test-session-003",
        },
    )

    assert response.status_code == 422
