import os
from uuid import UUID

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.document import Document
from app.schemas.document import DocumentListOut, DocumentOut
from app.storage import delete_file, upload_file

router = APIRouter()

ALLOWED_EXTENSIONS = {"docx", "xlsx", "pdf"}


def get_file_extension(filename: str) -> str:
    return filename.rsplit(".", 1)[-1].lower() if "." in filename else ""


@router.post("/upload", response_model=list[DocumentOut])
async def upload_documents(
    files: list[UploadFile] = File(...),
    document_type: str = "knowledge_base",
    db: AsyncSession = Depends(get_db),
):
    uploaded = []
    for file in files:
        ext = get_file_extension(file.filename or "")
        if ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(400, f"Unsupported file type: {ext}. Allowed: {', '.join(ALLOWED_EXTENSIONS)}")

        content = await file.read()
        file_path = await upload_file(content, file.filename or "unknown", file.content_type or "application/octet-stream")

        doc = Document(
            filename=file.filename or "unknown",
            file_type=ext,
            file_path=file_path,
            document_type=document_type,
        )
        db.add(doc)
        await db.flush()
        uploaded.append(doc)

    await db.commit()
    return uploaded


@router.get("", response_model=DocumentListOut)
async def list_documents(
    document_type: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    query = select(Document).order_by(Document.uploaded_at.desc())
    if document_type:
        query = query.where(Document.document_type == document_type)
    result = await db.execute(query)
    docs = list(result.scalars().all())
    return DocumentListOut(documents=docs, total=len(docs))


@router.delete("/{document_id}")
async def delete_document(document_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Document).where(Document.id == document_id))
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(404, "Document not found")

    await delete_file(doc.file_path)
    await db.delete(doc)
    await db.commit()
    return {"status": "deleted"}
