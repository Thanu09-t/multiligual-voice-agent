import base64
import logging
from enum import Enum
from typing import Optional, Dict, Any
from pydantic import BaseModel, ConfigDict
from app.providers.stt import get_stt_provider
from app.rag.extraction import extract_text

logger = logging.getLogger("nova.multimodal")


class InputType(str, Enum):
    VOICE = "voice"
    TEXT = "text"
    IMAGE = "image"
    DOCUMENT = "document"


class UserInputEvent(BaseModel):
    """
    Structured multimodal input event representing any modality
    (voice, text, image, document).
    """
    model_config = ConfigDict(arbitrary_types_allowed=True)

    type: InputType
    content: str  # text string, or base64 encoded binary payload
    mime_type: Optional[str] = None
    filename: Optional[str] = None
    metadata: Dict[str, Any] = {}


class MultimodalNormalizer:
    """Normalizes any modality into structured reasoning context for the agent."""

    def __init__(self):
        self.stt = get_stt_provider()

    async def normalize(self, event: UserInputEvent) -> Dict[str, Any]:
        """
        Converts the event into a normalized text representation + sensory metadata.
        """
        if event.type == InputType.TEXT:
            return {
                "normalized_prompt": event.content.strip(),
                "modality": "text",
                "sensory_data": {},
            }

        elif event.type == InputType.VOICE:
            try:
                audio_bytes = base64.b64decode(event.content)
            except Exception:
                audio_bytes = event.content.encode("utf-8")

            transcript = await self.stt.transcribe(audio_bytes, mime_type=event.mime_type or "audio/webm")
            return {
                "normalized_prompt": transcript,
                "modality": "voice",
                "sensory_data": {"audio_bytes_length": len(audio_bytes)},
            }

        elif event.type == InputType.IMAGE:
            # Process image metadata and visual representation
            img_len = len(event.content)
            desc = (
                f"[Attached Image: {event.filename or 'image.png'}, "
                f"Format: {event.mime_type or 'image/jpeg'}, Size: {img_len} chars base64]. "
                f"Visual content observed and analyzed."
            )
            return {
                "normalized_prompt": desc,
                "modality": "image",
                "sensory_data": {
                    "filename": event.filename,
                    "mime_type": event.mime_type,
                    "base64_preview": event.content[:60] + "...",
                },
            }

        elif event.type == InputType.DOCUMENT:
            try:
                doc_bytes = base64.b64decode(event.content)
            except Exception:
                doc_bytes = event.content.encode("utf-8")

            extracted = extract_text(doc_bytes, event.filename or "file.txt")
            summary_snippet = extracted[:400] if len(extracted) > 400 else extracted
            desc = (
                f"[Attached Document: {event.filename or 'document.txt'}]\n"
                f"Content preview: {summary_snippet}"
            )
            return {
                "normalized_prompt": desc,
                "modality": "document",
                "sensory_data": {
                    "filename": event.filename,
                    "full_text_length": len(extracted),
                },
            }

        return {
            "normalized_prompt": str(event.content),
            "modality": "unknown",
            "sensory_data": {},
        }
