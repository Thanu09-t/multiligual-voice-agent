import logging
from app.config import settings
from app.providers.base import TTSProvider
from app.providers.tts.mock import MockTTSProvider
from app.providers.tts.openai import OpenAITTSProvider

logger = logging.getLogger("nova.providers.tts")


def get_tts_provider() -> TTSProvider:
    provider_name = settings.TTS_PROVIDER.lower().strip()

    if provider_name == "openai" and settings.TTS_API_KEY:
        return OpenAITTSProvider(api_key=settings.TTS_API_KEY)
    else:
        if provider_name not in ["mock", ""]:
            logger.warning(
                f"TTS provider '{provider_name}' lacks API key or is unavailable. Falling back to MockTTSProvider."
            )
        return MockTTSProvider()
