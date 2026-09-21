from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from pydantic import BaseModel, ConfigDict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from app.database.database import get_db
from app.database.models import Conversation, Message

router = APIRouter(prefix="/conversations", tags=["Conversations"])


class ConversationCreate(BaseModel):
    title: Optional[str] = "New Conversation"
    user_id: str


class MessageOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    sender: str
    content: str
    spoken_content: Optional[str] = None
    created_at: str


class ConversationOut(BaseModel):
    id: str
    user_id: str
    title: str
    created_at: str
    updated_at: str
    messages: List[MessageOut] = []


@router.post("", response_model=ConversationOut)
async def create_conversation(payload: ConversationCreate, db: AsyncSession = Depends(get_db)):
    conv = Conversation(
        user_id=payload.user_id,
        title=payload.title or "New Conversation",
    )
    db.add(conv)
    await db.commit()
    await db.refresh(conv)
    return ConversationOut(
        id=conv.id,
        user_id=conv.user_id,
        title=conv.title,
        created_at=conv.created_at.isoformat(),
        updated_at=conv.updated_at.isoformat(),
        messages=[],
    )


@router.get("", response_model=List[ConversationOut])
async def list_conversations(user_id: Optional[str] = None, db: AsyncSession = Depends(get_db)):
    stmt = select(Conversation).order_by(desc(Conversation.updated_at))
    if user_id:
        stmt = stmt.where(Conversation.user_id == user_id)
    res = await db.execute(stmt)
    convs = res.scalars().all()
    out = []
    for c in convs:
        out.append(
            ConversationOut(
                id=c.id,
                user_id=c.user_id,
                title=c.title,
                created_at=c.created_at.isoformat(),
                updated_at=c.updated_at.isoformat(),
                messages=[],
            )
        )
    return out


@router.get("/{conversation_id}", response_model=ConversationOut)
async def get_conversation(conversation_id: str, db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(Conversation).where(Conversation.id == conversation_id))
    conv = res.scalar_one_or_none()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")

    msg_res = await db.execute(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.asc())
    )
    messages = msg_res.scalars().all()

    return ConversationOut(
        id=conv.id,
        user_id=conv.user_id,
        title=conv.title,
        created_at=conv.created_at.isoformat(),
        updated_at=conv.updated_at.isoformat(),
        messages=[
            MessageOut(
                id=m.id,
                sender=m.sender,
                content=m.content,
                spoken_content=m.spoken_content,
                created_at=m.created_at.isoformat(),
            )
            for m in messages
        ],
    )


@router.delete("/{conversation_id}")
async def delete_conversation(conversation_id: str, db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(Conversation).where(Conversation.id == conversation_id))
    conv = res.scalar_one_or_none()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    await db.delete(conv)
    await db.commit()
    return {"message": "Conversation deleted successfully", "id": conversation_id}
