import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.database.database import init_db


@pytest.mark.asyncio
async def test_transcribe_endpoint():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Create sample audio payload with test marker
        fake_audio = b"TEST_PROMPT: What is your name?\n" + b"\x00" * 200
        files = {"file": ("test.wav", fake_audio, "audio/wav")}
        resp = await client.post("/api/voice/transcribe", files=files)
        assert resp.status_code == 200
        data = resp.json()
        assert "transcript" in data
        assert len(data["transcript"]) > 0


@pytest.mark.asyncio
async def test_synthesize_endpoint():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.post(
            "/api/voice/synthesize",
            json={"text": "Hello, this is NOVA speaking."},
        )
        assert resp.status_code == 200
        assert resp.headers["content-type"] in ["audio/wav", "audio/mpeg"]
        audio_content = resp.content
        assert len(audio_content) > 100
        # Check standard RIFF WAV header if wav
        if resp.headers["content-type"] == "audio/wav":
            assert audio_content.startswith(b"RIFF")


@pytest.mark.asyncio
async def test_end_to_end_voice_interact():
    await init_db()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        fake_audio = b"TEST_PROMPT: Who are you?\n" + b"\x00" * 300
        files = {"file": ("mic_input.wav", fake_audio, "audio/wav")}
        data = {"user_id": "test-user-voice"}

        resp = await client.post("/api/voice/interact", files=files, data=data)
        assert resp.status_code == 200
        assert resp.headers["content-type"] in ["audio/wav", "audio/mpeg"]
        assert "X-Transcript" in resp.headers
        assert "X-Response-Text" in resp.headers
        assert len(resp.content) > 100
