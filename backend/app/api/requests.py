from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, File, HTTPException, UploadFile
from fastapi.responses import Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import async_session, get_db
from app.models.document import Document
from app.models.fill_request import FillRequest, FillRequestItem
from app.schemas.answer import FillRequestItemUpdate, FillRequestListOut, FillRequestOut
from app.services.ddq_filler import fill_ddq
from app.services.exporter import export_filled_ddq
from app.storage import upload_file

router = APIRouter()


async def _fill_in_background(fill_request_id: UUID):
    """Background task to fill a DDQ."""
    async with async_session() as db:
        try:
            await fill_ddq(fill_request_id, db)
        except Exception as e:
            print(f"Error filling DDQ {fill_request_id}: {e}")
            # Update status to indicate failure
            result = await db.execute(
                select(FillRequest).where(FillRequest.id == fill_request_id)
            )
            fr = result.scalar_one_or_none()
            if fr:
                fr.status = "error"
                await db.commit()


@router.post("", response_model=FillRequestOut)
async def create_fill_request(
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = None,
    db: AsyncSession = Depends(get_db),
):
    """Upload an unfilled DDQ and start the fill process."""
    ext = file.filename.rsplit(".", 1)[-1].lower() if file.filename and "." in file.filename else ""
    if ext not in {"docx", "xlsx", "pdf"}:
        raise HTTPException(400, f"Unsupported file type: {ext}")

    content = await file.read()
    file_path = await upload_file(content, file.filename or "unknown", file.content_type or "application/octet-stream")

    doc = Document(
        filename=file.filename or "unknown",
        file_type=ext,
        file_path=file_path,
        document_type="request",
    )
    db.add(doc)
    await db.flush()

    fill_request = FillRequest(document_id=doc.id, status="processing")
    db.add(fill_request)
    await db.commit()
    await db.refresh(fill_request)

    # Start fill process in background
    if background_tasks:
        background_tasks.add_task(_fill_in_background, fill_request.id)

    return FillRequestOut(
        id=fill_request.id,
        document_id=doc.id,
        document_filename=doc.filename,
        status=fill_request.status,
        items=[],
        created_at=fill_request.created_at,
        updated_at=fill_request.updated_at,
    )


@router.get("", response_model=FillRequestListOut)
async def list_fill_requests(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(FillRequest)
        .options(selectinload(FillRequest.document), selectinload(FillRequest.items))
        .order_by(FillRequest.created_at.desc())
    )
    requests = list(result.scalars().all())

    return FillRequestListOut(
        requests=[
            FillRequestOut(
                id=r.id,
                document_id=r.document_id,
                document_filename=r.document.filename if r.document else None,
                status=r.status,
                items=r.items,
                created_at=r.created_at,
                updated_at=r.updated_at,
            )
            for r in requests
        ],
        total=len(requests),
    )


@router.get("/{request_id}", response_model=FillRequestOut)
async def get_fill_request(request_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(FillRequest)
        .options(selectinload(FillRequest.document), selectinload(FillRequest.items))
        .where(FillRequest.id == request_id)
    )
    fr = result.scalar_one_or_none()
    if not fr:
        raise HTTPException(404, "Fill request not found")

    return FillRequestOut(
        id=fr.id,
        document_id=fr.document_id,
        document_filename=fr.document.filename if fr.document else None,
        status=fr.status,
        items=fr.items,
        created_at=fr.created_at,
        updated_at=fr.updated_at,
    )


@router.patch("/{request_id}/items/{item_id}")
async def update_fill_request_item(
    request_id: UUID,
    item_id: UUID,
    update: FillRequestItemUpdate,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(FillRequestItem).where(
            FillRequestItem.id == item_id,
            FillRequestItem.fill_request_id == request_id,
        )
    )
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "Item not found")

    if update.final_answer is not None:
        item.final_answer = update.final_answer
    if update.status is not None:
        item.status = update.status

    await db.commit()
    return {"status": "updated"}


@router.post("/{request_id}/approve")
async def approve_fill_request(request_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(FillRequest)
        .options(selectinload(FillRequest.items))
        .where(FillRequest.id == request_id)
    )
    fr = result.scalar_one_or_none()
    if not fr:
        raise HTTPException(404, "Fill request not found")

    # Set final_answer to suggested_answer for items that haven't been edited
    for item in fr.items:
        if not item.final_answer and item.suggested_answer:
            item.final_answer = item.suggested_answer
            item.status = "accepted"

    fr.status = "approved"
    await db.commit()
    return {"status": "approved"}


@router.post("/{request_id}/export")
async def export_fill_request(request_id: UUID, db: AsyncSession = Depends(get_db)):
    try:
        file_bytes, filename, content_type = await export_filled_ddq(request_id, db)
    except ValueError as e:
        raise HTTPException(404, str(e))

    # Update status
    result = await db.execute(select(FillRequest).where(FillRequest.id == request_id))
    fr = result.scalar_one_or_none()
    if fr:
        fr.status = "exported"
        await db.commit()

    return Response(
        content=file_bytes,
        media_type=content_type,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
