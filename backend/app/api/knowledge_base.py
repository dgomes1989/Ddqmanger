import asyncio
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import async_session, get_db
from app.models.document import Document
from app.models.question import Question
from app.schemas.answer import KnowledgeBaseStatsOut
from app.schemas.question import QuestionOut, QuestionWithAnswersOut
from app.services.knowledge_base import get_kb_stats, process_document, search_similar_questions

router = APIRouter()


async def _process_in_background(document_id: UUID):
    """Background task to process a document."""
    async with async_session() as db:
        try:
            await process_document(document_id, db)
        except Exception as e:
            print(f"Error processing document {document_id}: {e}")


@router.get("/stats", response_model=KnowledgeBaseStatsOut)
async def knowledge_base_stats(db: AsyncSession = Depends(get_db)):
    stats = await get_kb_stats(db)
    return KnowledgeBaseStatsOut(**stats)


@router.post("/process/{document_id}")
async def process_kb_document(
    document_id: UUID,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Document).where(Document.id == document_id))
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(404, "Document not found")
    if doc.processed:
        raise HTTPException(400, "Document already processed")

    background_tasks.add_task(_process_in_background, document_id)
    return {"status": "processing", "document_id": str(document_id)}


@router.post("/process-all")
async def process_all_documents(
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    """Process all unprocessed knowledge base documents."""
    result = await db.execute(
        select(Document).where(
            Document.document_type == "knowledge_base",
            Document.processed.is_(False),
        )
    )
    docs = list(result.scalars().all())
    for doc in docs:
        background_tasks.add_task(_process_in_background, doc.id)
    return {"status": "processing", "count": len(docs)}


@router.get("/questions", response_model=list[QuestionOut])
async def list_questions(
    search: str | None = None,
    category: str | None = None,
    limit: int = Query(50, le=200),
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
):
    query = select(Question).options(selectinload(Question.source_document))

    if category:
        query = query.where(Question.category == category)

    if search:
        query = query.where(Question.normalized_text.contains(search.lower()))

    query = query.order_by(Question.created_at.desc()).offset(offset).limit(limit)
    result = await db.execute(query)
    questions = list(result.scalars().all())

    return [
        QuestionOut(
            id=q.id,
            text=q.text,
            category=q.category,
            source_document_id=q.source_document_id,
            source_filename=q.source_document.filename if q.source_document else None,
            answers_count=0,
            created_at=q.created_at,
        )
        for q in questions
    ]


@router.get("/questions/{question_id}", response_model=QuestionWithAnswersOut)
async def get_question_with_answers(
    question_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Question)
        .options(
            selectinload(Question.answers),
            selectinload(Question.source_document),
        )
        .where(Question.id == question_id)
    )
    question = result.scalar_one_or_none()
    if not question:
        raise HTTPException(404, "Question not found")

    return question


@router.get("/search")
async def search_knowledge_base(
    query: str,
    limit: int = Query(5, le=20),
    db: AsyncSession = Depends(get_db),
):
    results = await search_similar_questions(query, db, limit=limit)
    return {"results": results}
