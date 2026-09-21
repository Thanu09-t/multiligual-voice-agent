from app.providers.base import STTProvider


class MockSTTProvider(STTProvider):
    """
    Intelligent mock STT provider for deterministic local testing
    and zero-cost offline validation.
    """

    async def transcribe(self, audio_bytes: bytes, mime_type: str = "audio/webm") -> str:
        if not audio_bytes:
            return ""

        # Check if the client embedded a test text marker in the audio payload header
        try:
            raw_prefix = audio_bytes[:100]
            if b"TEST_PROMPT:" in raw_prefix:
                start = raw_prefix.index(b"TEST_PROMPT:") + len(b"TEST_PROMPT:")
                end = raw_prefix.find(b"\n", start)
                if end == -1:
                    end = len(raw_prefix)
                return raw_prefix[start:end].decode("utf-8", errors="ignore").strip()
        except Exception:
            pass

        # Realistic default transcription
        return "Hello NOVA, what can you do for me?"
