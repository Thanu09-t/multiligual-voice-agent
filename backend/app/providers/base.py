from abc import ABC, abstractmethod
from typing import AsyncIterator, List, Dict, Any, Optional


class LLMProvider(ABC):
    """Abstract interface for LLM providers."""

    @abstractmethod
    async def generate(
        self,
        messages: List[Dict[str, str]],
        tools: Optional[List[Dict[str, Any]]] = None,
        temperature: float = 0.7,
    ) -> str:
        """Generate complete text response."""
        pass

    @abstractmethod
    async def stream_generate(
        self,
        messages: List[Dict[str, str]],
        tools: Optional[List[Dict[str, Any]]] = None,
        temperature: float = 0.7,
    ) -> AsyncIterator[str]:
        """Stream response tokens as they are produced."""
        pass


class STTProvider(ABC):
    """Abstract interface for Speech-to-Text providers."""

    @abstractmethod
    async def transcribe(self, audio_bytes: bytes, mime_type: str = "audio/webm") -> str:
        """Transcribe audio bytes to text transcript."""
        pass


class TTSProvider(ABC):
    """Abstract interface for Text-to-Speech providers."""

    @abstractmethod
    async def synthesize(self, text: str, voice: Optional[str] = None) -> bytes:
        """Synthesize text into audio bytes."""
        pass

    @abstractmethod
    async def stream_synthesize(
        self, text: str, voice: Optional[str] = None
    ) -> AsyncIterator[bytes]:
        """Stream synthesized audio chunks."""
        pass
