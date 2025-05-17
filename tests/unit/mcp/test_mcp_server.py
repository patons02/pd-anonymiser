import os
import sys
import pytest
from fastapi.testclient import TestClient

# Ensure the 'src' directory is on the path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

import mcp.mcp_server as server_module


@pytest.fixture(autouse=True)
def set_api_key(monkeypatch):
    # Ensure API key is set in environment
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")


def test_chat_success(monkeypatch):
    # Mock anonymisation
    dummy = server_module.AnonymisationResult(text="anon", session_id="sess", key="key")
    monkeypatch.setattr(
        server_module, "anonymise_text", lambda t, allow_reidentification: dummy
    )

    # Mock OpenAI response
    dummy_resp = {"choices": [{"message": {"content": "anon reply"}}]}
    fake_responses = type("R", (), {"create": lambda *args, **kwargs: dummy_resp})
    monkeypatch.setattr(server_module.openai, "responses", fake_responses)

    # Mock reidentification
    monkeypatch.setattr(server_module, "reidentify_text", lambda r, s, k: "real reply")

    client = TestClient(server_module.app)
    resp = client.post("/chat", json={"text": "Hello"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["original_text"] == "Hello"
    assert data["anonymised_text"] == "anon"
    assert data["gpt_response"] == "anon reply"
    assert data["reidentified_response"] == "real reply"


def test_chat_error(monkeypatch):
    dummy = server_module.AnonymisationResult(text="anon", session_id="sess", key="key")
    monkeypatch.setattr(
        server_module, "anonymise_text", lambda t, allow_reidentification: dummy
    )

    # Mock OpenAI to raise
    def raising(*args, **kwargs):
        raise Exception("API down")

    fake_responses = type("R", (), {"create": raising})
    monkeypatch.setattr(server_module.openai, "responses", fake_responses)

    client = TestClient(server_module.app)
    resp = client.post("/chat", json={"text": "Hello"})
    assert resp.status_code == 500
    data = resp.json()
    assert "error" in data
    assert data["original_text"] == "Hello"
    assert data["anonymised_text"] == "anon"


def test_openai_cost_endpoint(monkeypatch):
    # Patch cost functions
    monkeypatch.setattr(server_module, "count_tokens", lambda prompt, model: 2)
    monkeypatch.setattr(
        server_module,
        "estimate_cost",
        lambda prompt_tokens, max_completion_tokens, model: 0.123,
    )
    client = TestClient(server_module.app)
    resp = client.post(
        "/open-ai-cost",
        json={"prompt": "Hi", "model": "gpt-4", "max_completion_tokens": 10},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["prompt_token_count"] == 2
    assert data["cost"] == 0.123
