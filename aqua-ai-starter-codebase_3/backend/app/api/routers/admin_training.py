import shutil
import uuid
from pathlib import Path

from fastapi import APIRouter, BackgroundTasks, Depends, File, Form, UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.ingestion.pipeline import ingest_document
from app.api.deps import require_role
from app.db.session import AsyncSessionLocal, get_db
from app.models.document import DocumentStatus, KnowledgeDocument
from app.models.user import User, UserRole

router = APIRouter(prefix="/admin/documents", tags=["admin-training"])

UPLOAD_DIR = Path("app/ai/ingestion/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


async def _run_ingestion(document_id: uuid.UUID) -> None:
    """Runs in a fresh session since BackgroundTasks execute after the request's session closes."""
    async with AsyncSessionLocal() as db:
        await ingest_document(db, document_id)


@router.post("", status_code=202)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    title: str = Form(...),
    source_type: str = Form(...),  # pdf | csv | json | markdown | txt
    origin: str | None = Form(None),  # e.g. "WHO Hydration Guidelines 2023"
    dataset_version: str | None = Form(None),
    admin: User = Depends(require_role(UserRole.ADMIN, UserRole.RESEARCHER)),
    db: AsyncSession = Depends(get_db),
):
    """
    Upload a source document to the custom AI's knowledge base. Chunking,
    embedding, and vector indexing happen asynchronously — poll
    GET /admin/documents/{id} for status, or GET /admin/documents for the
    full training-monitor list.
    """
    dest = UPLOAD_DIR / f"{uuid.uuid4()}_{file.filename}"
    with dest.open("wb") as f:
        shutil.copyfileobj(file.file, f)

    doc = KnowledgeDocument(
        title=title,
        source_type=source_type,
        origin=origin,
        file_path=str(dest),
        status=DocumentStatus.UPLOADED,
        dataset_version=dataset_version,
        uploaded_by=admin.id,
    )
    db.add(doc)
    await db.commit()
    await db.refresh(doc)

    background_tasks.add_task(_run_ingestion, doc.id)
    return {"id": doc.id, "status": doc.status}


@router.get("")
async def list_documents(
    admin: User = Depends(require_role(UserRole.ADMIN, UserRole.RESEARCHER)),
    db: AsyncSession = Depends(get_db),
):
    """Training monitor: every document in the knowledge base and its indexing status."""
    docs = (await db.scalars(select(KnowledgeDocument).order_by(KnowledgeDocument.created_at.desc()))).all()
    return [
        {"id": d.id, "title": d.title, "status": d.status, "source_type": d.source_type,
         "dataset_version": d.dataset_version, "created_at": d.created_at}
        for d in docs
    ]


@router.delete("/{document_id}", status_code=204)
async def delete_document(
    document_id: uuid.UUID,
    admin: User = Depends(require_role(UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db),
):
    from app.ai.retrieval.vector_store import get_vector_store

    get_vector_store().delete_by_document(str(document_id))
    doc = await db.scalar(select(KnowledgeDocument).where(KnowledgeDocument.id == document_id))
    if doc:
        await db.delete(doc)
        await db.commit()
