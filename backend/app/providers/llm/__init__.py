import logging
from typing import AsyncIterator, List, Dict, Any, Optional
from app.config import settings
from app.providers.base import LLMProvider
from app.providers.llm.mock import MockLLMProvider
from app.providers.llm.openai import OpenAILLMProvider
from app.providers.llm.groq import GroqLLMProvider
from app.providers.llm.gemini import GeminiLLMProvider

logger = logging.getLogger("nova.providers.llm")


class ResilientLLMProvider(LLMProvider):
    """Resilient LLM wrapper that automatically falls back across active providers if rate-limited or unavailable."""

    def __init__(self, providers: List[LLMProvider]):
        self.providers = [p for p in providers if p is not None]

    async def generate(
        self,
        messages: List[Dict[str, str]],
        tools: Optional[List[Dict[str, Any]]] = None,
        temperature: float = 0.7,
    ) -> str:
        last_error = None
        for p in self.providers:
            try:
                return await p.generate(messages, tools=tools, temperature=temperature)
            except Exception as e:
                logger.warning(f"Provider '{p.__class__.__name__}' generate failed: {e}. Trying fallback...")
                last_error = e
        if last_error:
            logger.error(f"All LLM providers failed. Final error: {last_error}")
            mock = MockLLMProvider()
            return await mock.generate(messages, tools=tools, temperature=temperature)
        return ""

    async def stream_generate(
        self,
        messages: List[Dict[str, str]],
        tools: Optional[List[Dict[str, Any]]] = None,
        temperature: float = 0.7,
    ) -> AsyncIterator[str]:
        for p in self.providers:
            try:
                agen = p.stream_generate(messages, tools=tools, temperature=temperature)
                first = await agen.__anext__()

                async def _inner():
                    yield first
                    async for token in agen:
                        yield token

                async for tok in _inner():
                    yield tok
                return
            except StopAsyncIteration:
                return
            except Exception as e:
                logger.warning(f"Provider '{p.__class__.__name__}' stream_generate failed: {e}. Trying fallback...")
                continue

        mock = MockLLMProvider()
        async for tok in mock.stream_generate(messages, tools=tools, temperature=temperature):
            yield tok


def get_llm_provider() -> LLMProvider:
    provider_name = settings.LLM_PROVIDER.lower().strip()
    model = settings.LLM_MODEL or None

    chain: List[LLMProvider] = []

    # Primary provider
    if provider_name == "groq" and settings.GROQ_API_KEY:
        chain.append(GroqLLMProvider(api_key=settings.GROQ_API_KEY, model=model or "openai/gpt-oss-20b"))
        chain.append(GroqLLMProvider(api_key=settings.GROQ_API_KEY, model="qwen/qwen3.8-27b"))
    elif provider_name == "gemini" and settings.GEMINI_API_KEY:
        chain.append(GeminiLLMProvider(api_key=settings.GEMINI_API_KEY, model=model or "gemini-1.5-flash"))
    elif provider_name == "openai" and settings.OPENAI_API_KEY:
        chain.append(OpenAILLMProvider(api_key=settings.OPENAI_API_KEY, model=model or "gpt-4o-mini"))

    # Fallback live provider if another key is present
    if settings.GROQ_API_KEY and provider_name != "groq":
        chain.append(GroqLLMProvider(api_key=settings.GROQ_API_KEY, model="openai/gpt-oss-20b"))
    if settings.GEMINI_API_KEY and provider_name != "gemini":
        chain.append(GeminiLLMProvider(api_key=settings.GEMINI_API_KEY, model="gemini-1.5-flash"))
    if settings.OPENAI_API_KEY and provider_name != "openai":
        chain.append(OpenAILLMProvider(api_key=settings.OPENAI_API_KEY, model="gpt-4o-mini"))

    # Always end fallback chain with MockLLMProvider
    chain.append(MockLLMProvider())

    return ResilientLLMProvider(chain)
