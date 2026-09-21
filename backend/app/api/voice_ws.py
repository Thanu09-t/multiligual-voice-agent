import json
import base64
import asyncio
import logging
from typing import Optional
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.database import get_db
from app.config import settings
from app.agent.agent import NovaAgent
from app.agent.state import AgentStatus
from app.providers.stt import get_stt_provider
from app.providers.tts import get_tts_provider

logger = logging.getLogger("nova.voice_ws")
router = APIRouter(tags=["Voice WebSocket"])


class WebSocketSessionManager:
    """Manages an active real-time voice and streaming agent session."""

    def __init__(self, websocket: WebSocket, db: AsyncSession, user_id: Optional[str] = None):
        self.websocket = websocket
        self.db = db
        self.user_id = user_id
        self.agent = NovaAgent(db=db, user_id=user_id)
        self.stt = get_stt_provider()
        self.tts = get_tts_provider()
        self.audio_buffer = bytearray()
        self.current_task: Optional[asyncio.Task] = None
        self.active_conversation_id: Optional[str] = None

    async def send_event(self, event_type: str, data: dict):
        """Send a typed JSON event over WebSocket."""
        payload = {"type": event_type, **data}
        await self.websocket.send_text(json.dumps(payload))

    async def cancel_current_response(self):
        """Mandatory Barge-In: immediately interrupt ongoing generation and TTS."""
        if self.current_task and not self.current_task.done():
            self.current_task.cancel()
            self.current_task = None
            logger.info("Current agent task interrupted by user.")
            await self.send_event("interrupted", {"status": "INTERRUPTED"})
            await self.send_event("agent_status", {"status": AgentStatus.LISTENING.value})

    async def handle_audio_chunk(self, b64_chunk: str):
        """Buffer incoming PCM/WebM audio bytes."""
        try:
            chunk = base64.b64decode(b64_chunk)
            self.audio_buffer.extend(chunk)
        except Exception as e:
            logger.error(f"Error decoding audio chunk: {e}")

    async def handle_audio_data(self, b64_data: str, mime_type: str = "audio/webm"):
        """Direct complete audio recording payload from client MediaRecorder."""
        try:
            chunk = base64.b64decode(b64_data)
            self.audio_buffer = bytearray(chunk)
            await self.finalize_and_process_audio(mime_type=mime_type)
        except Exception as e:
            logger.error(f"Error handling direct audio payload: {e}")
            await self.send_event("agent_status", {"status": AgentStatus.IDLE.value})

    async def finalize_and_process_audio(self, mime_type: str = "audio/webm"):
        """When speech stops, finalize transcript and trigger agent reasoning."""
        if not self.audio_buffer or len(self.audio_buffer) < 400:
            self.audio_buffer.clear()
            await self.send_event("agent_status", {"status": AgentStatus.IDLE.value})
            return

        audio_bytes = bytes(self.audio_buffer)
        self.audio_buffer.clear()

        await self.send_event("agent_status", {"status": AgentStatus.THINKING.value})

        # 1. Transcribe audio
        try:
            transcript = await self.stt.transcribe(audio_bytes, mime_type=mime_type)
            cleaned = transcript.strip().strip(".").strip()

            # Filter common Whisper silence/breathing artifacts
            noise_hallucinations = {
                "", ".", "...", "you", "thank you", "thank you.",
                "thanks for watching", "subtitles by", "amara.org", "bye", "bye."
            }
            if not cleaned or cleaned.lower() in noise_hallucinations or len(cleaned) <= 1:
                logger.info(f"Ignoring silent/hallucinated transcript: '{cleaned}'")
                await self.send_event("agent_status", {"status": AgentStatus.IDLE.value})
                return

            logger.info(f"Recognized speech: '{transcript}'")
            await self.send_event("transcript_final", {"text": transcript})
        except Exception as e:
            logger.error(f"STT failed: {e}")
            await self.send_event("error", {"message": "Transcription failed."})
            await self.send_event("agent_status", {"status": AgentStatus.IDLE.value})
            return

        # 2. Start agent response task
        self.current_task = asyncio.create_task(self._generate_and_stream_response(transcript))

    async def handle_text_input(self, text: str):
        """Direct text input over WebSocket."""
        await self.cancel_current_response()
        await self.send_event("agent_status", {"status": AgentStatus.THINKING.value})
        self.current_task = asyncio.create_task(self._generate_and_stream_response(text))

    async def _generate_and_stream_response(self, user_text: str):
        """Execute tool planning and fast LLM reasoning, then stream response and TTS."""
        try:
            await self.send_event("agent_status", {"status": AgentStatus.THINKING.value})

            # Run complete agent turn: tools (calculator, weather, search, documents) + memory + LLM
            result = await self.agent.process_text(
                text=user_text,
                conversation_id=self.active_conversation_id,
            )

            if result.get("conversation_id"):
                self.active_conversation_id = result.get("conversation_id")

            display_text = result.get("display_text", "")
            spoken_text = result.get("spoken_text", display_text)
            tool_used = result.get("tool_used")

            # Immediately emit response_text so client displays message and starts speech synthesis with zero delay
            await self.send_event(
                "response_text",
                {
                    "display_text": display_text,
                    "spoken_text": spoken_text,
                    "tool_used": tool_used,
                    "conversation_id": self.active_conversation_id,
                },
            )
            await self.send_event("agent_status", {"status": AgentStatus.SPEAKING.value})

            # Stream TTS audio if a non-mock TTS provider is configured
            if settings.TTS_PROVIDER not in ("mock", ""):
                chunk_idx = 0
                async for audio_chunk in self.tts.stream_synthesize(spoken_text):
                    b64_audio = base64.b64encode(audio_chunk).decode("utf-8")
                    await self.send_event(
                        "tts_audio_chunk",
                        {"data": b64_audio, "index": chunk_idx, "is_final": False},
                    )
                    chunk_idx += 1
                await self.send_event("tts_audio_chunk", {"data": "", "index": chunk_idx, "is_final": True})

        except asyncio.CancelledError:
            logger.info("Response generation cancelled by interruption.")
        except Exception as e:
            logger.error(f"Error generating response: {e}", exc_info=True)
            await self.send_event("error", {"message": "An error occurred generating response."})
            await self.send_event("agent_status", {"status": AgentStatus.ERROR.value})


@router.websocket("/voice")
async def voice_websocket(
    websocket: WebSocket,
    user_id: Optional[str] = None,
    conversation_id: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    """
    Bi-directional streaming WebSocket voice protocol.
    Supports audio streaming, token streaming, TTS streaming, and instant barge-in.
    """
    await websocket.accept()
    session = WebSocketSessionManager(websocket=websocket, db=db, user_id=user_id)
    session.active_conversation_id = conversation_id

    await session.send_event("agent_status", {"status": AgentStatus.IDLE.value})

    try:
        while True:
            message_raw = await websocket.receive_text()
            try:
                msg = json.loads(message_raw)
            except json.JSONDecodeError:
                continue

            event_type = msg.get("type")

            # 1. Speech started -> instant barge-in
            if event_type == "speech_started":
                await session.cancel_current_response()
                await session.send_event("agent_status", {"status": AgentStatus.LISTENING.value})

            # 2. Complete Audio Data payload from client MediaRecorder
            elif event_type == "audio_data":
                await session.handle_audio_data(
                    b64_data=msg.get("data", ""),
                    mime_type=msg.get("mime_type", "audio/webm"),
                )

            # 3. Audio chunk
            elif event_type == "audio_chunk":
                await session.handle_audio_chunk(msg.get("data", ""))

            # 4. Speech stopped -> finalize audio and reason
            elif event_type == "speech_stopped":
                await session.finalize_and_process_audio()

            # 5. Explicit user interruption
            elif event_type == "interrupt":
                await session.cancel_current_response()

            # 6. Text input
            elif event_type == "text_input":
                await session.handle_text_input(msg.get("text", ""))

    except WebSocketDisconnect:
        logger.info("WebSocket voice client disconnected.")
        if session.current_task:
            session.current_task.cancel()
