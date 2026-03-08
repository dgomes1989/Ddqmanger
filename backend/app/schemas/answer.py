from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class FillRequestItemOut(BaseModel):
    id: UUID
    question_text: str
    question_index: int
    suggested_answer: str | None
    final_answer: str | None
    has_conflict: bool
    conflicting_answers: list[dict] | None = None
    status: str

    model_config = {"from_attributes": True}


class FillRequestItemUpdate(BaseModel):
    final_answer: str | None = None
    status: str | None = None


class FillRequestOut(BaseModel):
    id: UUID
    document_id: UUID
    document_filename: str | None = None
    status: str
    items: list[FillRequestItemOut] = []
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class FillRequestListOut(BaseModel):
    requests: list[FillRequestOut]
    total: int


class KnowledgeBaseStatsOut(BaseModel):
    total_documents: int
    processed_documents: int
    total_questions: int
    total_answers: int
