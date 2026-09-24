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
        raw_user_message = ""
        for m in reversed(messages):
            if m.get("role") == "user":
                raw_user_message = m.get("content", "")
                break

        if not raw_user_message.strip():
            return "Hello! I am NOVA. How can I help you today?"

        import re

        # Handle search context synthesis prompts gracefully in mock mode
        if "context information:" in raw_user_message.lower():
            m_ctx = re.search(r"Context information:\s*\n([\s\S]*?)(?:\n\nUser question:|$)", raw_user_message, re.IGNORECASE)
            if m_ctx:
                ctx_text = m_ctx.group(1).strip()
                # Extract first 1-2 meaningful sentences from context
                sentences = re.split(r"(?<=[.!?])\s+", ctx_text)
                clean_sentences = [s.strip() for s in sentences if len(s.strip()) > 15]
                if clean_sentences:
                    return " ".join(clean_sentences[:2])

        last_user_message = raw_user_message.lower().strip()

        # Pure greeting (exact word match, not substring match like 'which' or 'think')
        if re.search(r"^(?:hello|hi|hey|greetings|good\s+(?:morning|afternoon|evening))\b", last_user_message):
            # If the user only said a greeting
            if len(last_user_message.split()) <= 4:
                return "Hello! I am NOVA, your voice-first AI agent. How can I assist you right now?"

        if "who are you" in last_user_message or "what are you" in last_user_message:
            return "I am NOVA, a voice-first AI agent that listens, reasons, remembers, and acts."

        if "deepest ocean" in last_user_message or "mariana trench" in last_user_message:
            return "The Mariana Trench in the western Pacific Ocean is the deepest part of the ocean, reaching a depth of nearly 11,000 meters (36,000 feet)."

        if "capital of france" in last_user_message:
            return "The capital of France is Paris."

        if "calculate" in last_user_message or "+" in last_user_message or "*" in last_user_message:
            return "I can compute that for you accurately."

        if "weather" in last_user_message:
            return "I can check the live weather report for you."

        return f"I understand your query about '{raw_user_message.strip()}'. As NOVA, I am ready to process your request."

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
