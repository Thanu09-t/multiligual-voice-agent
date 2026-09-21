import base64
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.database.database import init_db
from app.agent.multimodal import UserInputEvent, InputType, MultimodalNormalizer


@pytest.mark.asyncio
async def test_multimodal_normalizer():
    norm = MultimodalNormalizer()

    # 1. Text Event
    e_text = UserInputEvent(type=InputType.TEXT, content="Hello from text event")
    res_text = await norm.normalize(e_text)
    assert res_text["modality"] == "text"
    assert res_text["normalized_prompt"] == "Hello from text event"

    # 2. Image Event
    dummy_b64_img = base64.b64encode(b"FAKE_IMAGE_BYTES").decode()
    e_img = UserInputEvent(
        type=InputType.IMAGE,
        content=dummy_b64_img,
        filename="diagram.png",
        mime_type="image/png",
    )
    res_img = await norm.normalize(e_img)
    assert res_img["modality"] == "image"
    assert "diagram.png" in res_img["normalized_prompt"]

    # 3. Document Event
    dummy_doc = base64.b64encode(b"This is an attached document content.").decode()
    e_doc = UserInputEvent(
        type=InputType.DOCUMENT,
        content=dummy_doc,
        filename="specs.txt",
    )
    res_doc = await norm.normalize(e_doc)
    assert res_doc["modality"] == "document"
    assert "specs.txt" in res_doc["normalized_prompt"]


@pytest.mark.asyncio
async def test_multimodal_chat_api():
    await init_db()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Send image analysis request
        dummy_img = base64.b64encode(b"PNG_MOCK_DATA").decode()
        resp = await client.post(
            "/api/chat/multimodal",
            json={
                "type": "image",
                "content": dummy_img,
                "filename": "screenshot.png",
                "mime_type": "image/png",
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["display_text"]) > 0
        assert data["agent_status"] == "IDLE"
