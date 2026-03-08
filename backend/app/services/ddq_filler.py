"""DDQ fill pipeline: parse unfilled DDQ, match answers from KB, detect conflicts."""

import json
from uuid import UUID

import anthropic
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.document import Document
from app.models.fill_request import FillRequest, FillRequestItem
from app.services.document_parser import parse_document
from app.services.knowledge_base import search_similar_questions
from app.services.qa_extractor import extract_questions_only
from app.storage import download_file

ANSWER_SELECTION_PROMPT = """You are helping fill a Due Diligence Questionnaire (DDQ) for an investment fund.

Given a question from the DDQ and several candidate answers from previous DDQs, select or synthesize the best answer.

Rules:
- Prefer the most recent answer when answers are similar
- If answers are substantially different (conflicting), note that
- The answer should be professional and suitable for an investor DDQ
- Do not make up information - only use what's provided in the candidate answers

Question: {question}

Candidate answers (from most recent to oldest):
{candidates}

Return a JSON object with:
- "answer": The best answer text
- "has_conflict": true if candidates have substantially different/conflicting answers, false otherwise
- "confidence": A score from 0.0 to 1.0 indicating confidence in the answer
- "conflicting_answers": If has_conflict is true, an array of objects with "text" and "source" for each conflicting answer

Return ONLY the JSON object, no other text."""


async def fill_ddq(fill_request_id: UUID, db: AsyncSession):
    """Process an unfilled DDQ: extract questions, match answers, detect conflicts."""
    result = await db.execute(
        select(FillRequest).where(FillRequest.id == fill_request_id)
    )
    fill_request = result.scalar_one_or_none()
    if not fill_request:
        raise ValueError(f"Fill request {fill_request_id} not found")

    # Get the document
    doc_result = await db.execute(
        select(Document).where(Document.id == fill_request.document_id)
    )
    doc = doc_result.scalar_one_or_none()
    if not doc:
        raise ValueError("Document not found")

    # Parse and extract questions
    file_bytes = await download_file(doc.file_path)
    raw_text = parse_document(file_bytes, doc.file_type)
    doc.raw_text = raw_text

    questions = await extract_questions_only(raw_text)

    client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)

    for idx, q in enumerate(questions):
        question_text = q.get("question", "").strip()
        if not question_text:
            continue

        # Search knowledge base for similar questions
        similar = await search_similar_questions(question_text, db, limit=5)

        # Collect all candidate answers
        all_candidates = []
        for match in similar:
            for ans in match["answers"]:
                all_candidates.append({
                    "text": ans["text"],
                    "source": ans["source_filename"] or "Unknown",
                    "date": ans["answered_at"] or "Unknown",
                })

        suggested_answer = None
        has_conflict = False
        conflicting_answers = None

        if all_candidates:
            # Use Claude to select/synthesize the best answer
            candidates_text = "\n".join(
                f"- [{c['source']}, {c['date']}]: {c['text']}" for c in all_candidates
            )

            message = await client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=2048,
                messages=[
                    {
                        "role": "user",
                        "content": ANSWER_SELECTION_PROMPT.format(
                            question=question_text, candidates=candidates_text
                        ),
                    }
                ],
            )

            response_text = message.content[0].text.strip()
            if response_text.startswith("```"):
                response_text = response_text.split("\n", 1)[1].rsplit("```", 1)[0].strip()

            try:
                result_data = json.loads(response_text)
                suggested_answer = result_data.get("answer")
                has_conflict = result_data.get("has_conflict", False)
                if has_conflict:
                    conflicting_answers = result_data.get("conflicting_answers", [])
            except json.JSONDecodeError:
                suggested_answer = all_candidates[0]["text"] if all_candidates else None

        item = FillRequestItem(
            fill_request_id=fill_request.id,
            question_text=question_text,
            question_index=idx,
            suggested_answer=suggested_answer,
            has_conflict=has_conflict,
            conflicting_answers=conflicting_answers,
            status="pending" if suggested_answer else "flagged",
        )
        db.add(item)

    fill_request.status = "draft"
    doc.processed = True
    await db.commit()
