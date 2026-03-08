import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class FillRequest(Base):
    __tablename__ = "fill_requests"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("documents.id"))
    status: Mapped[str] = mapped_column(String(20), default="processing")  # processing, draft, approved, exported
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    document = relationship("Document")
    items = relationship("FillRequestItem", back_populates="fill_request", cascade="all, delete-orphan",
                         order_by="FillRequestItem.question_index")


class FillRequestItem(Base):
    __tablename__ = "fill_request_items"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    fill_request_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("fill_requests.id"))
    question_text: Mapped[str] = mapped_column(Text)
    question_index: Mapped[int] = mapped_column(Integer)
    suggested_answer: Mapped[str | None] = mapped_column(Text, nullable=True)
    final_answer: Mapped[str | None] = mapped_column(Text, nullable=True)
    has_conflict: Mapped[bool] = mapped_column(Boolean, default=False)
    conflicting_answers: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="pending")  # pending, accepted, edited, flagged

    fill_request = relationship("FillRequest", back_populates="items")
