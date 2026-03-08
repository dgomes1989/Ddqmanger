from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class DocumentOut(BaseModel):
    id: UUID
    filename: str
    file_type: str
    document_type: str
    uploaded_at: datetime
    processed: bool

    model_config = {"from_attributes": True}


class DocumentListOut(BaseModel):
    documents: list[DocumentOut]
    total: int
