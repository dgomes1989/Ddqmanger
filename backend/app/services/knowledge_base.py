"""Knowledge base service: process documents, store Q&A, and search."""

import re
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.answer import Answer
from app.models.document import Document
from app.models.question import Question
from app.services.document_parser import parse_document
from app.services.embedding import generate_embedding
from app.services.qa_extractor import extract_qa_pairs
from app.storage import download_file


def normalize_question(text: str) -> str:
    """Normalize question text for better matching."""
    text = text.lower().strip()
    text = re.sub(r"[^\w\s]", "", text)
    text = re.sub(r"\s+", " ", text)
    return text


async def process_document(document_id: UUID, db: AsyncSession):
    """Process a knowledge base document: parse, extract Q&A, store with embeddings."""
    result = await db.execute(select(Document).where(Document.id == document_id))
    doc = result.scalar_one_or_none()
    if not doc:
        raise ValueError(f"Document {document_id} not found")

    # Download and parse
    file_bytes = await download_file(doc.file_path)
    raw_text = parse_document(file_bytes, doc.file_type)
    doc.raw_text = raw_text

    # Extract Q&A pairs using Claude
    qa_pairs = await extract_qa_pairs(raw_text)

    for pair in qa_pairs:
        question_text = pair.get("question", "").strip()
        answer_text = pair.get("answer")
        category = pair.get("category")

        if not question_text:
            continue

        normalized = normalize_question(question_text)

        # Generate embedding for the question
        embedding = await generate_embedding(question_text)

        question = Question(
            text=question_text,
            normalized_text=normalized,
            embedding=embedding if embedding else None,
            source_document_id=doc.id,
            category=category,
        )
        db.add(question)
        await db.flush()

        if answer_text and answer_text.strip():
            answer = Answer(
                question_id=question.id,
                text=answer_text.strip(),
                source_document_id=doc.id,
                answered_at=doc.uploaded_at,
            )
            db.add(answer)

    doc.processed = True
    await db.commit()


async def search_similar_questions(
    query_text: str, db: AsyncSession, limit: int = 5
) -> list[dict]:
    """Search for similar questions in the knowledge base."""
    query_embedding = await generate_embedding(query_text)

    if query_embedding:
        # Semantic search using pgvector
        result = await db.execute(
            select(Question)
            .options(selectinload(Question.answers).selectinload(Answer.source_document))
            .options(selectinload(Question.source_document))
            .where(Question.embedding.isnot(None))
            .order_by(Question.embedding.cosine_distance(query_embedding))
            .limit(limit)
        )
        questions = list(result.scalars().all())
    else:
        # Fallback: text-based search
        normalized = normalize_question(query_text)
        keywords = normalized.split()[:5]
        conditions = [Question.normalized_text.contains(kw) for kw in keywords if len(kw) > 2]

        if conditions:
            from sqlalchemy import or_
            result = await db.execute(
                select(Question)
                .options(selectinload(Question.answers).selectinload(Answer.source_document))
                .options(selectinload(Question.source_document))
                .where(or_(*conditions))
                .limit(limit)
            )
            questions = list(result.scalars().all())
        else:
            questions = []

    results = []
    for q in questions:
        answers_data = []
        for a in q.answers:
            answers_data.append({
                "id": str(a.id),
                "text": a.text,
                "source_filename": a.source_document.filename if a.source_document else None,
                "confidence": a.confidence,
                "answered_at": a.answered_at.isoformat() if a.answered_at else None,
            })
        # Sort answers by date (most recent first)
        answers_data.sort(key=lambda x: x["answered_at"] or "", reverse=True)

        results.append({
            "question_id": str(q.id),
            "question_text": q.text,
            "category": q.category,
            "source_filename": q.source_document.filename if q.source_document else None,
            "answers": answers_data,
        })

    return results


async def get_kb_stats(db: AsyncSession) -> dict:
    """Get knowledge base statistics."""
    total_docs = await db.scalar(
        select(func.count()).select_from(Document).where(Document.document_type == "knowledge_base")
    )
    processed_docs = await db.scalar(
        select(func.count()).select_from(Document).where(
            Document.document_type == "knowledge_base", Document.processed.is_(True)
        )
    )
    total_questions = await db.scalar(select(func.count()).select_from(Question))
    total_answers = await db.scalar(select(func.count()).select_from(Answer))

    return {
        "total_documents": total_docs or 0,
        "processed_documents": processed_docs or 0,
        "total_questions": total_questions or 0,
        "total_answers": total_answers or 0,
    }
