import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    filename: Mapped[str] = mapped_column(String(500))
    file_type: Mapped[str] = mapped_column(String(10))  # docx, xlsx, pdf
    file_path: Mapped[str] = mapped_column(String(1000))  # S3 path
    document_type: Mapped[str] = mapped_column(String(20))  # knowledge_base, request
    uploaded_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    processed: Mapped[bool] = mapped_column(Boolean, default=False)
    metadata_: Mapped[dict | None] = mapped_column("metadata", JSONB, nullable=True)
    raw_text: Mapped[str | None] = mapped_column(Text, nullable=True)

    questions = relationship("Question", back_populates="source_document", cascade="all, delete-orphan")
    answers = relationship("Answer", back_populates="source_document", cascade="all, delete-orphan")
