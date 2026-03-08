from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class AnswerOut(BaseModel):
    id: UUID
    text: str
    source_document_id: UUID
    source_filename: str | None = None
    confidence: float
    answered_at: datetime | None
    is_approved: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class QuestionOut(BaseModel):
    id: UUID
    text: str
    category: str | None
    source_document_id: UUID
    source_filename: str | None = None
    answers_count: int = 0
    created_at: datetime

    model_config = {"from_attributes": True}


class QuestionWithAnswersOut(QuestionOut):
    answers: list[AnswerOut] = []
