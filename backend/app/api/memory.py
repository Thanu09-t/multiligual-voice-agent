from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, ConfigDict
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.database import get_db
from app.memory.long_term import LongTermMemoryManager

router = APIRouter(prefix="/memory", tags=["Memory"])


class MemoryCreate(BaseModel):
    user_id: str
    category: Optional[str] = "preference"
    key: str
    value: str


class MemoryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    category: str
    key: str
    value: str
    confidence: float
    created_at: str
    updated_at: str


@router.get("", response_model=List[MemoryOut])
async def list_memories(user_id: str = Query(..., description="User ID"), db: AsyncSession = Depends(get_db)):
    mgr = LongTermMemoryManager(db=db, user_id=user_id)
    memories = await mgr.list_all()
    return [
        MemoryOut(
            id=m.id,
            user_id=m.user_id,
            category=m.category,
            key=m.key,
            value=m.value,
            confidence=m.confidence,
            created_at=m.created_at.isoformat(),
            updated_at=m.updated_at.isoformat(),
        )
        for m in memories
    ]


@router.post("", response_model=MemoryOut)
async def create_memory(payload: MemoryCreate, db: AsyncSession = Depends(get_db)):
    mgr = LongTermMemoryManager(db=db, user_id=payload.user_id)
    mem = await mgr.save_memory(
        category=payload.category or "preference",
        key=payload.key,
        value=payload.value,
    )
    return MemoryOut(
        id=mem.id,
        user_id=mem.user_id,
        category=mem.category,
        key=mem.key,
        value=mem.value,
        confidence=mem.confidence,
        created_at=mem.created_at.isoformat(),
        updated_at=mem.updated_at.isoformat(),
    )


@router.delete("/{memory_id}")
async def delete_memory(memory_id: str, user_id: str = Query(...), db: AsyncSession = Depends(get_db)):
    mgr = LongTermMemoryManager(db=db, user_id=user_id)
    success = await mgr.delete_memory(memory_id)
    if not success:
        raise HTTPException(status_code=404, detail="Memory item not found.")
    return {"message": "Memory deleted successfully", "id": memory_id}


@router.delete("")
async def clear_all_memories(
    user_id: str = Query(...),
    category: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    mgr = LongTermMemoryManager(db=db, user_id=user_id)
    count = await mgr.clear_all(category=category)
    return {"message": f"Cleared {count} memory items."}
