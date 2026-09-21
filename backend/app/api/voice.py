import logging
from typing import Optional
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, Response
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.database import get_db
from app.agent.agent import NovaAgent
from app.providers.stt import get_stt_provider
from app.providers.tts import get_tts_provider

logger = logging.getLogger("nova.voice")
router = APIRouter(prefix="/voice", tags=["Voice"])


class SynthesizeRequest(BaseModel):
    text: str
    voice: Optional[str] = None


@router.post("/transcribe")
async def transcribe_audio(file: UploadFile = File(...)):
    """Transcribe uploaded audio file to text."""
    audio_bytes = await file.read()
    if not audio_bytes:
        raise HTTPException(status_code=400, detail="Empty audio file provided.")

    stt = get_stt_provider()
    try:
        transcript = await stt.transcribe(audio_bytes, mime_type=file.content_type or "audio/webm")
        return {"transcript": transcript}
    except Exception as e:
        logger.error(f"STT Error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Speech transcription failed.")


@router.post("/synthesize")
async def synthesize_text(payload: SynthesizeRequest):
    """Synthesize text to audio stream."""
    if not payload.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty.")

    tts = get_tts_provider()
    try:
        audio_bytes = await tts.synthesize(payload.text, voice=payload.voice)
        # Determine media type (wav for mock synthetic, mp3 for openai)
        media_type = "audio/wav" if audio_bytes.startswith(b"RIFF") else "audio/mpeg"
        return Response(content=audio_bytes, media_type=media_type)
    except Exception as e:
        logger.error(f"TTS Error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Text-to-speech synthesis failed.")


@router.post("/interact")
async def voice_interaction(
    file: UploadFile = File(...),
    conversation_id: Optional[str] = Form(None),
    user_id: Optional[str] = Form(None),
    db: AsyncSession = Depends(get_db),
):
    """
    End-to-end voice loop:
    User Audio -> STT -> Agent (LLM) -> TTS -> Spoken Audio Response.
    """
    audio_bytes = await file.read()
    if not audio_bytes:
        raise HTTPException(status_code=400, detail="Empty audio payload.")

    # 1. Transcribe speech
    stt = get_stt_provider()
    transcript = await stt.transcribe(audio_bytes, mime_type=file.content_type or "audio/webm")

    # 2. Agent reasoning
    agent = NovaAgent(db=db, user_id=user_id)
    chat_res = await agent.process_text(text=transcript, conversation_id=conversation_id)

    # 3. Synthesize speech
    tts = get_tts_provider()
    speech_audio = await tts.synthesize(chat_res["spoken_text"])
    media_type = "audio/wav" if speech_audio.startswith(b"RIFF") else "audio/mpeg"

    # 4. Return audio with transcript and response headers (safely encoded for HTTP headers)
    import urllib.parse
    safe_transcript = transcript.replace("\n", " ").encode("ascii", "ignore").decode("ascii")
    safe_response = chat_res["display_text"].replace("\n", " ").encode("ascii", "ignore").decode("ascii")
    headers = {
        "X-Transcript": safe_transcript,
        "X-Response-Text": safe_response,
        "X-Conversation-Id": str(chat_res["conversation_id"] or ""),
    }
    return Response(content=speech_audio, media_type=media_type, headers=headers)
