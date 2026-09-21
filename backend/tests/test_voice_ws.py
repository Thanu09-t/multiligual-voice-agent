import json
import pytest
from starlette.testclient import TestClient
from app.main import app
from app.database.database import init_db


def test_websocket_text_and_streaming():
    client = TestClient(app)
    with client.websocket_connect("/api/voice") as websocket:
        # 1. Initial status event
        data = websocket.receive_json()
        assert data["type"] == "agent_status"
        assert data["status"] == "IDLE"

        # 2. Send text input
        websocket.send_json({"type": "text_input", "text": "Hello NOVA"})

        # 3. Read events until response_text
        received_types = []
        for _ in range(30):
            event = websocket.receive_json()
            received_types.append(event["type"])
            if event["type"] == "response_text":
                assert isinstance(event["display_text"], str) and len(event["display_text"].strip()) > 0
                break

        assert "agent_status" in received_types
        assert "response_text" in received_types


def test_websocket_barge_in_interruption():
    client = TestClient(app)
    with client.websocket_connect("/api/voice") as websocket:
        # Initial event
        websocket.receive_json()

        # Start generating a response
        websocket.send_json({"type": "text_input", "text": "Tell me a long story"})

        # Immediate interrupt event
        websocket.send_json({"type": "interrupt"})

        # Verify interrupted confirmation
        interrupted = False
        for _ in range(15):
            event = websocket.receive_json()
            if event["type"] == "interrupted":
                interrupted = True
                break

        assert interrupted is True
