import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings

client = TestClient(app)

def test_health_check():
    """
    Verify the health endpoint is working correctly.
    """
    response = client.get(f"{settings.API_V1_STR}/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "version" in data

def test_chat_endpoint_schema():
    """
    Verify the chat endpoint accepts requests and returns the correct response schema.
    """
    payload = {
        "message": "Hello",
        "history": []
    }
    response = client.post(f"{settings.API_V1_STR}/chat", json=payload)
    assert response.status_code == 200
    data = response.json()
    
    # Verify strict schema compliance
    assert "reply" in data
    assert "recommendations" in data
    assert isinstance(data["recommendations"], list)
    assert "end_of_conversation" in data
    assert isinstance(data["end_of_conversation"], bool)

def test_chat_invalid_payload():
    """
    Verify the chat endpoint rejects invalid payloads.
    """
    payload = {
        "msg": "Invalid key"
    }
    response = client.post(f"{settings.API_V1_STR}/chat", json=payload)
    assert response.status_code == 422  # Unprocessable Entity
