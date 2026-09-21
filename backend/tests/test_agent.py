import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.database.database import init_db


@pytest.mark.asyncio
async def test_text_agent_chat_and_conversation():
    await init_db()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # 1. Create conversation
        conv_resp = await client.post(
            "/api/conversations",
            json={"title": "Test Chat", "user_id": "user-123"},
        )
        assert conv_resp.status_code == 200
        conv_data = conv_resp.json()
        conv_id = conv_data["id"]
        assert conv_data["title"] == "Test Chat"

        # 2. Chat with agent
        chat_resp = await client.post(
            "/api/chat",
            json={
                "message": "Hello NOVA, who are you?",
                "conversation_id": conv_id,
                "user_id": "user-123",
            },
        )
        assert chat_resp.status_code == 200
        chat_data = chat_resp.json()
        assert len(chat_data["display_text"].strip()) > 0
        assert chat_data["agent_status"] == "IDLE"

        # 3. Retrieve conversation history to ensure persistence
        get_conv_resp = await client.get(f"/api/conversations/{conv_id}")
        assert get_conv_resp.status_code == 200
        history_data = get_conv_resp.json()
        assert len(history_data["messages"]) >= 2
        assert history_data["messages"][0]["sender"] == "user"
        assert history_data["messages"][1]["sender"] == "agent"
