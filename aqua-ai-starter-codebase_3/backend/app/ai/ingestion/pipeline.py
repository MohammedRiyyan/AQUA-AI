"""
End-to-end ingestion pipeline invoked by the admin training module whenever
a new source (research paper, WHO/CDC PDF, hydration dataset, etc.) is
uploaded. Runs as a background task so the upload request returns
immediately; status is tracked on KnowledgeDocument.status.

    upload -> load_document() -> chunk_text() -> embed_texts() -> vector_store.upsert()

This same pipeline is what "Retrain / Version datasets" in the admin UI
triggers — re-running it against the full corpus rebuilds the index from
scratch under a new dataset_version tag.
"""
import logging
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.ingestion.chunker import chunk_text
from app.ai.ingestion.loaders import load_document
from app.ai.retrieval.embeddings import embed_texts
from app.ai.retrieval.vector_store import get_vector_store
from app.models.document import DocumentChunk, DocumentStatus, KnowledgeDocument

logger = logging.getLogger("aqua_ai.ingestion")


async def ingest_document(db: AsyncSession, document_id: uuid.UUID) -> None:
    doc = await db.scalar(select(KnowledgeDocument).where(KnowledgeDocument.id == document_id))
    if doc is None:
        logger.error("ingest_document called for missing document_id=%s", document_id)
        return

    try:
        doc.status = DocumentStatus.CHUNKING
        await db.commit()

        raw_text = load_document(doc.file_path, doc.source_type)
        chunks = chunk_text(raw_text)
        if not chunks:
            doc.status = DocumentStatus.FAILED
            await db.commit()
            return

        doc.status = DocumentStatus.EMBEDDING
        await db.commit()

        vectors = embed_texts(chunks)
        store = get_vector_store()

        vector_ids, metadata, chunk_rows = [], [], []
        for i, (chunk, _vec) in enumerate(zip(chunks, vectors, strict=True)):
            vid = f"{doc.id}:{i}"
            vector_ids.append(vid)
            metadata.append(
                {
                    "vector_id": vid,
                    "text": chunk,
                    "document_id": str(doc.id),
                    "document_title": doc.origin or doc.title,
                    "chunk_index": i,
                }
            )
            chunk_rows.append(DocumentChunk(document_id=doc.id, chunk_index=i, text=chunk, vector_id=vid))

        store.upsert(vector_ids, vectors, metadata)
        db.add_all(chunk_rows)

        doc.status = DocumentStatus.INDEXED
        await db.commit()
        logger.info("Indexed %d chunks for document %s (%s)", len(chunks), doc.title, doc.id)

    except Exception:
        logger.exception("Ingestion failed for document %s", document_id)
        doc.status = DocumentStatus.FAILED
        await db.commit()
