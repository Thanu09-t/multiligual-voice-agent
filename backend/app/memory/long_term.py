import re
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from app.database.models import Memory


class LongTermMemoryManager:
    """Manages persistent long-term memories with extraction and retrieval."""

    def __init__(self, db: AsyncSession, user_id: str):
        self.db = db
        self.user_id = user_id

    def extract_memories(self, text: str) -> List[Dict[str, str]]:
        """
        Analyze user message to detect high-value permanent facts/preferences.
        Does NOT store random conversational chatter.
        """
        extracted = []

        # 1. Project name
        project_match = re.search(r"(?:my\s+project\s+is\s+(?:called\s+)?|the\s+project\s+name\s+is\s+)([\w\-\.\_]+)", text, re.IGNORECASE)
        if project_match:
            extracted.append({
                "category": "project",
                "key": "project_name",
                "value": project_match.group(1).strip().rstrip(".?!,"),
            })

        # 2. User name
        name_match = re.search(r"(?:my\s+name\s+is\s+|call\s+me\s+)([\w\s]{2,25})", text, re.IGNORECASE)
        if name_match:
            name = name_match.group(1).strip().rstrip(".?!,")
            if not any(w in name.lower() for w in ["what", "who", "why", "how"]):
                extracted.append({
                    "category": "persona",
                    "key": "user_name",
                    "value": name,
                })

        # 3. User preference
        pref_match = re.search(r"(?:i\s+prefer\s+|my\s+preference\s+is\s+)([\w\s\+\#\.\-]+)", text, re.IGNORECASE)
        if pref_match:
            extracted.append({
                "category": "preference",
                "key": "preference",
                "value": pref_match.group(1).strip().rstrip(".?!,"),
            })

        # 4. Explicit "Remember that..."
        rem_match = re.search(r"(?:remember\s+(?:that\s+)?)(.*)", text, re.IGNORECASE)
        if rem_match:
            fact = rem_match.group(1).strip().rstrip(".?!,")
            extracted.append({
                "category": "fact",
                "key": f"fact_{abs(hash(fact)) % 10000}",
                "value": fact,
            })

        return extracted

    async def save_memory(self, category: str, key: str, value: str) -> Memory:
        """Upsert memory for this user."""
        stmt = select(Memory).where(Memory.user_id == self.user_id, Memory.key == key)
        res = await self.db.execute(stmt)
        existing = res.scalar_one_or_none()

        if existing:
            existing.value = value
            existing.category = category
            await self.db.commit()
            await self.db.refresh(existing)
            return existing
        else:
            mem = Memory(
                user_id=self.user_id,
                category=category,
                key=key,
                value=value,
            )
            self.db.add(mem)
            await self.db.commit()
            await self.db.refresh(mem)
            return mem

    async def get_relevant_memories(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Retrieve memories relevant to the query words or general user profile."""
        stmt = select(Memory).where(Memory.user_id == self.user_id)
        res = await self.db.execute(stmt)
        memories = res.scalars().all()

        words = set(query.lower().split())
        matched = []
        unmatched = []

        for m in memories:
            item = {"id": m.id, "category": m.category, "key": m.key, "value": m.value}
            # Score relevance
            val_words = set(m.value.lower().split()) | {m.key.lower()}
            if words & val_words:
                matched.append(item)
            else:
                unmatched.append(item)

        # Prioritize matching memories, fill remaining with general facts
        combined = matched + unmatched
        return combined[:limit]

    async def list_all(self) -> List[Memory]:
        stmt = select(Memory).where(Memory.user_id == self.user_id).order_by(Memory.updated_at.desc())
        res = await self.db.execute(stmt)
        return list(res.scalars().all())

    async def delete_memory(self, memory_id: str) -> bool:
        stmt = select(Memory).where(Memory.id == memory_id, Memory.user_id == self.user_id)
        res = await self.db.execute(stmt)
        mem = res.scalar_one_or_none()
        if mem:
            await self.db.delete(mem)
            await self.db.commit()
            return True
        return False

    async def clear_all(self, category: Optional[str] = None) -> int:
        stmt = delete(Memory).where(Memory.user_id == self.user_id)
        if category:
            stmt = stmt.where(Memory.category == category)
        res = await self.db.execute(stmt)
        await self.db.commit()
        return res.rowcount
