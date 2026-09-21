import io
import zipfile
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.database.database import init_db
from app.rag.extraction import extract_text, extract_text_from_docx, extract_text_from_txt
from app.rag.chunking import chunk_text
from app.rag.embeddings import generate_embedding, cosine_similarity


def test_txt_and_docx_extraction():
    # TXT
    raw_txt = b"NOVA is an AI voice operating interface."
    assert "voice operating" in extract_text_from_txt(raw_txt)

    # In-memory minimal DOCX
    bio = io.BytesIO()
    with zipfile.ZipFile(bio, "w") as zf:
        xml = (
            b'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            b'<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
            b'<w:body><w:p><w:r><w:t>Project AutoTrust Overview Document</w:t></w:r></w:p></w:body>'
            b'</w:document>'
        )
        zf.writestr("word/document.xml", xml)
    docx_bytes = bio.getvalue()
    extracted = extract_text_from_docx(docx_bytes)
    assert "AutoTrust Overview" in extracted


def test_chunking_and_embeddings():
    long_text = "This is a section about neural networks. " * 30
    chunks = chunk_text(long_text, chunk_size=150, chunk_overlap=30)
    assert len(chunks) > 1

    emb1 = generate_embedding("Neural networks and deep learning")
    emb2 = generate_embedding("Deep learning and artificial intelligence")
    emb3 = generate_embedding("Cooking chocolate chip cookies")

    sim_related = cosine_similarity(emb1, emb2)
    sim_unrelated = cosine_similarity(emb1, emb3)
    assert sim_related > sim_unrelated


@pytest.mark.asyncio
async def test_rag_upload_and_search_api():
    await init_db()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # 1. Upload document
        file_content = (
            b"NOVA Architecture Blueprint.\n"
            b"NOVA uses WebSockets for real-time streaming speech.\n"
            b"It supports instant barge-in via client-side VAD.\n"
            b"Long-term memory is persisted in PostgreSQL."
        )
        files = {"file": ("architecture_doc.txt", file_content, "text/plain")}
        data = {"user_id": "test-rag-user"}

        up_resp = await client.post("/api/documents/upload", files=files, data=data)
        assert up_resp.status_code == 200
        doc_data = up_resp.json()
        assert doc_data["status"] == "indexed"
        assert doc_data["chunk_count"] >= 1
        doc_id = doc_data["id"]

        # 2. List documents
        list_resp = await client.get("/api/documents?user_id=test-rag-user")
        assert list_resp.status_code == 200
        docs = list_resp.json()
        assert any(d["id"] == doc_id for d in docs)

        # 3. Search document chunks
        search_resp = await client.post(
            "/api/documents/search",
            json={"user_id": "test-rag-user", "query": "barge-in VAD speech"},
        )
        assert search_resp.status_code == 200
        matches = search_resp.json()["matches"]
        assert len(matches) > 0
        assert "barge-in" in matches[0]["text"].lower()

        # 4. Delete document
        del_resp = await client.delete(f"/api/documents/{doc_id}")
        assert del_resp.status_code == 200
