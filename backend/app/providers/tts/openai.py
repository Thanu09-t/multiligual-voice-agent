import httpx
from typing import AsyncIterator, Optional
from app.providers.base import TTSProvider


class OpenAITTSProvider(TTSProvider):
    """OpenAI Text-to-Speech API provider."""

    def __init__(self, api_key: str, model: str = "tts-1", default_voice: str = "nova"):
        self.api_key = api_key
        self.model = model
        self.default_voice = default_voice

    async def synthesize(self, text: str, voice: Optional[str] = None) -> bytes:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model,
            "input": text,
            "voice": voice or self.default_voice,
            "response_format": "mp3",
        }
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                "https://api.openai.com/v1/audio/speech",
                headers=headers,
                json=payload,
            )
            resp.raise_for_status()
            return resp.content

    async def stream_synthesize(
        self, text: str, voice: Optional[str] = None
    ) -> AsyncIterator[bytes]:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model,
            "input": text,
            "voice": voice or self.default_voice,
            "response_format": "mp3",
        }
        async with httpx.AsyncClient(timeout=30.0) as client:
            async with client.stream(
                "POST",
                "https://api.openai.com/v1/audio/speech",
                headers=headers,
                json=payload,
            ) as resp:
                resp.raise_for_status()
                async for chunk in resp.aiter_bytes(chunk_size=4096):
                    yield chunk
