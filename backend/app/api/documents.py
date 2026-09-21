from typing import List, Optional
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, Query
from pydantic import BaseModel, ConfigDict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database.database import get_db
from app.database.models import Document, DocumentChunk
from app.rag.pipeline import RAGPipeline
from app.rag.retrieval import RAGRetriever

router = APIRouter(prefix="/documents", tags=["Documents & RAG"])


class DocumentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    filename: str
    file_type: str
    file_size: int
    status: str
    chunk_count: int
    error_message: Optional[str] = None
    created_at: str


class SearchRequest(BaseModel):
    query: str
    user_id: str
    top_k: Optional[int] = 3


@router.post("/upload", response_model=DocumentOut)
async def upload_document(
    file: UploadFile = File(...),
    user_id: str = Form(...),
    db: AsyncSession = Depends(get_db),
):
    """Upload and index PDF, TXT, or DOCX document."""
    file_bytes = await file.read()
    if not file_bytes:
        raise HTTPException(status_code=400, detail="Empty file uploaded.")

    # Size limit: 15MB
    if len(file_bytes) > 15 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File exceeds 15MB limit.")

    pipeline = RAGPipeline(db=db)
    doc = await pipeline.ingest_document(
        user_id=user_id,
        filename=file.filename or "uploaded_document.txt",
        file_bytes=file_bytes,
        content_type=file.content_type or "text/plain",
    )

    return DocumentOut(
        id=doc.id,
        user_id=doc.user_id,
        filename=doc.filename,
        file_type=doc.file_type,
        file_size=doc.file_size,
        status=doc.status,
        chunk_count=doc.chunk_count,
        error_message=doc.error_message,
        created_at=doc.created_at.isoformat(),
    )


@router.get("", response_model=List[DocumentOut])
async def list_documents(user_id: str = Query(...), db: AsyncSession = Depends(get_db)):
    """List all documents for a user."""
    stmt = select(Document).where(Document.user_id == user_id).order_by(Document.created_at.desc())
    res = await db.execute(stmt)
    docs = res.scalars().all()
    return [
        DocumentOut(
            id=d.id,
            user_id=d.user_id,
            filename=d.filename,
            file_type=d.file_type,
            file_size=d.file_size,
            status=d.status,
            chunk_count=d.chunk_count,
            error_message=d.error_message,
            created_at=d.created_at.isoformat(),
        )
        for d in docs
    ]


@router.get("/{document_id}/chunks")
async def get_document_chunks(document_id: str, db: AsyncSession = Depends(get_db)):
    """Inspect chunks of a document."""
    stmt = (
        select(DocumentChunk)
        .where(DocumentChunk.document_id == document_id)
        .order_by(DocumentChunk.chunk_index.asc())
    )
    res = await db.execute(stmt)
    chunks = res.scalars().all()
    return [
        {
            "chunk_index": c.chunk_index,
            "text": c.text_content,
            "has_embedding": bool(c.embedding),
        }
        for c in chunks
    ]


@router.delete("/{document_id}")
async def delete_document(document_id: str, db: AsyncSession = Depends(get_db)):
    """Delete document and all associated chunks."""
    stmt = select(Document).where(Document.id == document_id)
    res = await db.execute(stmt)
    doc = res.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")

    await db.delete(doc)
    await db.commit()
    return {"message": "Document deleted successfully", "id": document_id}


@router.post("/search")
async def search_documents(payload: SearchRequest, db: AsyncSession = Depends(get_db)):
    """Semantic vector search across uploaded user documents."""
    retriever = RAGRetriever(db=db, user_id=payload.user_id)
    matches = await retriever.retrieve(query=payload.query, top_k=payload.top_k or 3)
    return {"query": payload.query, "matches": matches}
