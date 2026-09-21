import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.database.database import init_db
from app.memory.short_term import ShortTermMemoryManager
from app.memory.long_term import LongTermMemoryManager


def test_short_term_memory_sliding_window():
    stm = ShortTermMemoryManager(max_recent_messages=4)
    messages = [
        {"role": "user", "content": f"Message {i}"} for i in range(10)
    ]
    res = stm.manage_context(messages)
    assert len(res["active_messages"]) == 4
    assert res["summary"] is not None
    assert "Message 0" in res["summary"]


def test_long_term_memory_extraction():
    ltm = LongTermMemoryManager(db=None, user_id="test-user")
    
    facts1 = ltm.extract_memories("My project is called AutoTrust.")
    assert len(facts1) >= 1
    assert facts1[0]["key"] == "project_name"
    assert facts1[0]["value"] == "AutoTrust"

    facts2 = ltm.extract_memories("My name is Sarah Connor.")
    assert len(facts2) >= 1
    assert facts2[0]["key"] == "user_name"
    assert "Sarah Connor" in facts2[0]["value"]


@pytest.mark.asyncio
async def test_memory_crud_api():
    await init_db()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # 1. Create memory
        create_resp = await client.post(
            "/api/memory",
            json={
                "user_id": "test-user-crud",
                "category": "project",
                "key": "framework",
                "value": "FastAPI and Next.js",
            },
        )
        assert create_resp.status_code == 200
        mem_id = create_resp.json()["id"]

        # 2. List memories
        list_resp = await client.get("/api/memory?user_id=test-user-crud")
        assert list_resp.status_code == 200
        items = list_resp.json()
        assert len(items) >= 1
        assert any(m["id"] == mem_id for m in items)

        # 3. Delete memory
        del_resp = await client.delete(f"/api/memory/{mem_id}?user_id=test-user-crud")
        assert del_resp.status_code == 200

        # 4. Verify deletion
        list_resp2 = await client.get("/api/memory?user_id=test-user-crud")
        assert all(m["id"] != mem_id for m in list_resp2.json())


@pytest.mark.asyncio
async def test_agent_auto_memory_extraction_via_chat():
    await init_db()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Tell agent user's project
        chat_resp = await client.post(
            "/api/chat",
            json={
                "message": "My project is called AutoTrust.",
                "user_id": "user-auto-mem",
            },
        )
        assert chat_resp.status_code == 200

        # Check that memory was automatically saved
        mem_resp = await client.get("/api/memory?user_id=user-auto-mem")
        assert mem_resp.status_code == 200
        memories = mem_resp.json()
        assert any(m["key"] == "project_name" and m["value"] == "AutoTrust" for m in memories)
