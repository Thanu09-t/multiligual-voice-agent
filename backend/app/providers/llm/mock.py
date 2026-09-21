import asyncio
from typing import AsyncIterator, List, Dict, Any, Optional
from app.providers.base import LLMProvider


class MockLLMProvider(LLMProvider):
    """
    Intelligent mock LLM provider for zero-cost testing, fallback,
    and offline operation.
    """

    async def generate(
        self,
        messages: List[Dict[str, str]],
        tools: Optional[List[Dict[str, Any]]] = None,
        temperature: float = 0.7,
    ) -> str:
        last_user_message = ""
        for m in reversed(messages):
            if m.get("role") == "user":
                last_user_message = m.get("content", "").lower()
                break

        if not last_user_message:
            return "Hello! I am NOVA. How can I help you today?"

        if "hello" in last_user_message or "hi" in last_user_message:
            return "Hello! I am NOVA, your voice-first AI agent. How can I assist you right now?"

        if "who are you" in last_user_message or "what are you" in last_user_message:
            return "I am NOVA, a voice-first AI agent that listens, reasons, remembers, and acts."

        if "calculate" in last_user_message or "+" in last_user_message or "*" in last_user_message:
            return "I can compute that for you accurately."

        if "weather" in last_user_message:
            return "I can check the live weather report for you."

        return f"I understand: '{last_user_message}'. As NOVA, I am ready to process your request."

    async def stream_generate(
        self,
        messages: List[Dict[str, str]],
        tools: Optional[List[Dict[str, Any]]] = None,
        temperature: float = 0.7,
    ) -> AsyncIterator[str]:
        full_text = await self.generate(messages, tools, temperature)
        words = full_text.split(" ")
        for i, word in enumerate(words):
            chunk = word if i == len(words) - 1 else word + " "
            yield chunk
            await asyncio.sleep(0.04)  # Simulate real token stream cadence
