import logging
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.models import Document, DocumentChunk
from app.rag.extraction import extract_text
from app.rag.chunking import chunk_text
from app.rag.embeddings import generate_embedding

logger = logging.getLogger("nova.rag.pipeline")


class RAGPipeline:
    """End-to-end ingestion and indexing pipeline for documents."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def ingest_document(
        self,
        user_id: str,
        filename: str,
        file_bytes: bytes,
        content_type: str = "text/plain",
    ) -> Document:
        """
        Process document:
        Document -> Text Extraction -> Cleaning -> Chunking -> Embedding -> Vector DB.
        """
        ext = filename.split(".")[-1].lower() if "." in filename else "txt"

        doc = Document(
            user_id=user_id,
            filename=filename,
            file_type=ext,
            file_size=len(file_bytes),
            status="processing",
        )
        self.db.add(doc)
        await self.db.commit()
        await self.db.refresh(doc)

        try:
            # 1. Extract text
            raw_text = extract_text(file_bytes, filename)
            if not raw_text.strip():
                raise ValueError("No extractable text found in document.")

            # 2. Chunk text
            chunks = chunk_text(raw_text, chunk_size=400, chunk_overlap=80)

            # 3. Embed and store chunks
            chunk_records = []
            for i, chunk_str in enumerate(chunks):
                emb = generate_embedding(chunk_str)
                chunk_rec = DocumentChunk(
                    document_id=doc.id,
                    chunk_index=i,
                    text_content=chunk_str,
                    embedding=emb,
                    metadata_json={"filename": filename, "chunk_index": i},
                )
                chunk_records.append(chunk_rec)

            self.db.add_all(chunk_records)
            doc.chunk_count = len(chunk_records)
            doc.status = "indexed"
            await self.db.commit()
            await self.db.refresh(doc)
            logger.info(f"Document {filename} indexed successfully with {len(chunk_records)} chunks.")
            return doc

        except Exception as e:
            logger.error(f"Error ingesting document {filename}: {e}", exc_info=True)
            doc.status = "error"
            doc.error_message = str(e)
            await self.db.commit()
            await self.db.refresh(doc)
            return doc
