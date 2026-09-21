import logging
from app.config import settings
from app.providers.base import STTProvider
from app.providers.stt.mock import MockSTTProvider
from app.providers.stt.whisper import WhisperSTTProvider

logger = logging.getLogger("nova.providers.stt")


def get_stt_provider() -> STTProvider:
    provider_name = settings.STT_PROVIDER.lower().strip()

    if provider_name == "whisper" and settings.STT_API_KEY:
        return WhisperSTTProvider(api_key=settings.STT_API_KEY)
    elif provider_name == "groq" and (settings.GROQ_API_KEY or settings.STT_API_KEY):
        key = settings.GROQ_API_KEY or settings.STT_API_KEY
        return WhisperSTTProvider(
            api_key=key,
            model="whisper-large-v3-turbo",
            base_url="https://api.groq.com/openai/v1/audio/transcriptions",
        )
    else:
        if provider_name not in ["mock", ""]:
            logger.warning(
                f"STT provider '{provider_name}' lacks API key or is unavailable. Falling back to MockSTTProvider."
            )
        return MockSTTProvider()
