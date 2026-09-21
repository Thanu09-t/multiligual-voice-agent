from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.database import get_db
from app.agent.agent import NovaAgent

router = APIRouter(prefix="/chat", tags=["Chat"])


class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None
    user_id: Optional[str] = None


class ChatResponse(BaseModel):
    conversation_id: Optional[str]
    display_text: str
    spoken_text: str
    agent_status: str


@router.post("", response_model=ChatResponse)
async def chat(request: ChatRequest, db: AsyncSession = Depends(get_db)):
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty.")

    agent = NovaAgent(db=db, user_id=request.user_id)
    result = await agent.process_text(
        text=request.message,
        conversation_id=request.conversation_id,
    )
    return ChatResponse(
        conversation_id=result.get("conversation_id"),
        display_text=result.get("display_text", ""),
        spoken_text=result.get("spoken_text", ""),
        agent_status=result.get("agent_status", "IDLE"),
    )


class MultimodalChatRequest(BaseModel):
    type: str  # voice, text, image, document
    content: str
    filename: Optional[str] = None
    mime_type: Optional[str] = None
    conversation_id: Optional[str] = None
    user_id: Optional[str] = None


@router.post("/multimodal", response_model=ChatResponse)
async def multimodal_chat(request: MultimodalChatRequest, db: AsyncSession = Depends(get_db)):
    from app.agent.multimodal import UserInputEvent, InputType

    event = UserInputEvent(
        type=InputType(request.type.lower()),
        content=request.content,
        filename=request.filename,
        mime_type=request.mime_type,
    )

    agent = NovaAgent(db=db, user_id=request.user_id)
    result = await agent.process_multimodal_event(
        event=event,
        conversation_id=request.conversation_id,
    )

    return ChatResponse(
        conversation_id=result.get("conversation_id"),
        display_text=result.get("display_text", ""),
        spoken_text=result.get("spoken_text", ""),
        agent_status=result.get("agent_status", "IDLE"),
    )
