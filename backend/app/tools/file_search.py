from typing import Any, Dict, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.tools.base import BaseTool
from app.database.models import DocumentChunk, Document


class FileSearchTool(BaseTool):
    """Document search tool for querying uploaded files."""

    name = "search_documents"
    description = "Search through user-uploaded documents and files for relevant passages."
    parameters = {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Keywords or search phrases to find within uploaded files.",
            }
        },
        "required": ["query"],
    }
    requires_confirmation = False

    def __init__(self, db: AsyncSession, user_id: str = None):
        self.db = db
        self.user_id = user_id

    async def execute(self, query: str, **kwargs) -> Any:
        if not self.db:
            return {"query": query, "matches": []}

        # Query chunks matching query text
        stmt = select(DocumentChunk).where(DocumentChunk.text_content.ilike(f"%{query}%")).limit(4)
        res = await self.db.execute(stmt)
        chunks = res.scalars().all()

        matches = []
        for c in chunks:
            matches.append({
                "chunk_id": c.id,
                "document_id": c.document_id,
                "text": c.text_content[:300],
            })

        return {
            "query": query,
            "matches_found": len(matches),
            "results": matches,
        }
