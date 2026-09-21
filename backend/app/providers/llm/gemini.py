import json
import httpx
from typing import AsyncIterator, List, Dict, Any, Optional
from app.providers.base import LLMProvider


class GeminiLLMProvider(LLMProvider):
    """Google Gemini REST API implementation."""

    def __init__(self, api_key: str, model: str = "gemini-3.6-flash"):
        self.api_key = api_key
        self.model = model
        self.base_url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}"

    def _convert_messages(self, messages: List[Dict[str, str]]) -> tuple[Optional[Dict[str, Any]], List[Dict[str, Any]]]:
        system_instruction = None
        contents = []
        for m in messages:
            role = m.get("role", "user")
            content_text = m.get("content", "")
            if role == "system" and not system_instruction:
                system_instruction = {"parts": [{"text": content_text}]}
            else:
                conv_role = "user" if role in ["user", "system"] else "model"
                contents.append({"role": conv_role, "parts": [{"text": content_text}]})
        return system_instruction, contents

    async def generate(
        self,
        messages: List[Dict[str, str]],
        tools: Optional[List[Dict[str, Any]]] = None,
        temperature: float = 0.7,
    ) -> str:
        system_instruction, contents = self._convert_messages(messages)
        payload: Dict[str, Any] = {
            "contents": contents,
            "generationConfig": {"temperature": temperature},
        }
        if system_instruction:
            payload["system_instruction"] = system_instruction

        headers = {"User-Agent": "NOVA-Agent/1.0", "Content-Type": "application/json"}
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                f"{self.base_url}:generateContent?key={self.api_key}",
                headers=headers,
                json=payload,
            )
            resp.raise_for_status()
            data = resp.json()
            candidates = data.get("candidates", [])
            if candidates and "content" in candidates[0]:
                parts = candidates[0]["content"].get("parts", [])
                return "".join([p.get("text", "") for p in parts])
            return ""

    async def stream_generate(
        self,
        messages: List[Dict[str, str]],
        tools: Optional[List[Dict[str, Any]]] = None,
        temperature: float = 0.7,
    ) -> AsyncIterator[str]:
        # Gemini streaming
        system_instruction, contents = self._convert_messages(messages)
        payload: Dict[str, Any] = {
            "contents": contents,
            "generationConfig": {"temperature": temperature},
        }
        if system_instruction:
            payload["system_instruction"] = system_instruction

        headers = {"User-Agent": "NOVA-Agent/1.0", "Content-Type": "application/json"}
        async with httpx.AsyncClient(timeout=30.0) as client:
            async with client.stream(
                "POST",
                f"{self.base_url}:streamGenerateContent?key={self.api_key}&alt=sse",
                headers=headers,
                json=payload,
            ) as resp:
                resp.raise_for_status()
                async for line in resp.aiter_lines():
                    if not line or not line.startswith("data: "):
                        continue
                    try:
                        data = json.loads(line[6:])
                        candidates = data.get("candidates", [])
                        if candidates and "content" in candidates[0]:
                            parts = candidates[0]["content"].get("parts", [])
                            text = "".join([p.get("text", "") for p in parts])
                            if text:
                                yield text
                    except Exception:
                        continue
