from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database.models import Document, DocumentChunk
from app.rag.embeddings import generate_embedding, cosine_similarity


class RAGRetriever:
    """Retrieves top-k relevant document chunks using vector cosine similarity."""

    def __init__(self, db: AsyncSession, user_id: str):
        self.db = db
        self.user_id = user_id

    async def retrieve(
        self,
        query: str,
        top_k: int = 3,
        similarity_threshold: float = 0.25,
    ) -> List[Dict[str, Any]]:
        """Retrieve most relevant document chunks for query."""
        query_emb = generate_embedding(query)

        # Get all chunks for this user's indexed documents
        stmt = (
            select(DocumentChunk, Document)
            .join(Document, DocumentChunk.document_id == Document.id)
            .where(Document.user_id == self.user_id, Document.status == "indexed")
        )
        res = await self.db.execute(stmt)
        rows = res.all()

        scored_chunks = []
        for chunk, doc in rows:
            if not chunk.embedding:
                continue
            sim = cosine_similarity(query_emb, chunk.embedding)
            if sim >= similarity_threshold:
                scored_chunks.append({
                    "chunk_id": chunk.id,
                    "document_id": doc.id,
                    "filename": doc.filename,
                    "chunk_index": chunk.chunk_index,
                    "text": chunk.text_content,
                    "score": round(sim, 4),
                })

        # Sort by score descending
        scored_chunks.sort(key=lambda x: x["score"], reverse=True)
        return scored_chunks[:top_k]
