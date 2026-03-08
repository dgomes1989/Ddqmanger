"""Initial schema

Revision ID: 001
Revises:
Create Date: 2026-03-08

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Enable pgvector extension
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    op.create_table(
        "documents",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("filename", sa.String(500), nullable=False),
        sa.Column("file_type", sa.String(10), nullable=False),
        sa.Column("file_path", sa.String(1000), nullable=False),
        sa.Column("document_type", sa.String(20), nullable=False),
        sa.Column("uploaded_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("processed", sa.Boolean, default=False),
        sa.Column("metadata", postgresql.JSONB, nullable=True),
        sa.Column("raw_text", sa.Text, nullable=True),
    )

    op.create_table(
        "questions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("text", sa.Text, nullable=False),
        sa.Column("normalized_text", sa.Text, nullable=False),
        sa.Column("embedding", sa.Column.__class__, nullable=True),  # pgvector handled separately
        sa.Column("source_document_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("documents.id"), nullable=False),
        sa.Column("category", sa.String(100), nullable=True),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    )
    # Add vector column separately for pgvector
    op.execute("ALTER TABLE questions ADD COLUMN IF NOT EXISTS embedding vector(1024)")

    op.create_table(
        "answers",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("question_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("questions.id"), nullable=False),
        sa.Column("text", sa.Text, nullable=False),
        sa.Column("source_document_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("documents.id"), nullable=False),
        sa.Column("confidence", sa.Float, default=1.0),
        sa.Column("answered_at", sa.DateTime, nullable=True),
        sa.Column("is_approved", sa.Boolean, default=False),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    )

    op.create_table(
        "fill_requests",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("document_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("documents.id"), nullable=False),
        sa.Column("status", sa.String(20), default="processing"),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, server_default=sa.func.now()),
    )

    op.create_table(
        "fill_request_items",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("fill_request_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("fill_requests.id"), nullable=False),
        sa.Column("question_text", sa.Text, nullable=False),
        sa.Column("question_index", sa.Integer, nullable=False),
        sa.Column("suggested_answer", sa.Text, nullable=True),
        sa.Column("final_answer", sa.Text, nullable=True),
        sa.Column("has_conflict", sa.Boolean, default=False),
        sa.Column("conflicting_answers", postgresql.JSONB, nullable=True),
        sa.Column("status", sa.String(20), default="pending"),
    )

    # Indexes
    op.create_index("ix_documents_type", "documents", ["document_type"])
    op.create_index("ix_questions_source", "questions", ["source_document_id"])
    op.create_index("ix_answers_question", "answers", ["question_id"])
    op.create_index("ix_fill_items_request", "fill_request_items", ["fill_request_id"])


def downgrade() -> None:
    op.drop_table("fill_request_items")
    op.drop_table("fill_requests")
    op.drop_table("answers")
    op.drop_table("questions")
    op.drop_table("documents")
