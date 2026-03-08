"""Export filled DDQ back to Word, Excel, or PDF format."""

import io
from uuid import UUID

import docx
from docx.shared import Pt
import openpyxl
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.fill_request import FillRequest


async def export_filled_ddq(fill_request_id: UUID, db: AsyncSession) -> tuple[bytes, str, str]:
    """Export a filled DDQ. Returns (file_bytes, filename, content_type)."""
    result = await db.execute(
        select(FillRequest)
        .options(selectinload(FillRequest.items), selectinload(FillRequest.document))
        .where(FillRequest.id == fill_request_id)
    )
    fill_request = result.scalar_one_or_none()
    if not fill_request:
        raise ValueError("Fill request not found")

    doc = fill_request.document
    original_type = doc.file_type

    items = sorted(fill_request.items, key=lambda x: x.question_index)

    if original_type == "xlsx":
        return _export_xlsx(items, doc.filename)
    else:
        # Default to Word for both docx and pdf (PDF can be converted from Word)
        return _export_docx(items, doc.filename)


def _export_docx(items, original_filename: str) -> tuple[bytes, str, str]:
    """Export as Word document."""
    document = docx.Document()

    # Title
    title = document.add_heading("DDQ Response", level=0)

    for item in items:
        # Question
        q_para = document.add_paragraph()
        q_run = q_para.add_run(f"Q{item.question_index + 1}: {item.question_text}")
        q_run.bold = True
        q_run.font.size = Pt(11)

        # Answer
        answer = item.final_answer or item.suggested_answer or "[No answer provided]"
        a_para = document.add_paragraph(answer)
        a_para.style.font.size = Pt(10)

        # Add spacing
        document.add_paragraph()

    buffer = io.BytesIO()
    document.save(buffer)
    buffer.seek(0)

    filename = original_filename.rsplit(".", 1)[0] + "_filled.docx"
    return buffer.read(), filename, "application/vnd.openxmlformats-officedocument.wordprocessingml.document"


def _export_xlsx(items, original_filename: str) -> tuple[bytes, str, str]:
    """Export as Excel workbook."""
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "DDQ Responses"

    # Headers
    ws.cell(row=1, column=1, value="#")
    ws.cell(row=1, column=2, value="Question")
    ws.cell(row=1, column=3, value="Answer")
    ws.cell(row=1, column=4, value="Status")

    # Bold headers
    for col in range(1, 5):
        ws.cell(row=1, column=col).font = openpyxl.styles.Font(bold=True)

    # Data
    for idx, item in enumerate(items, start=2):
        ws.cell(row=idx, column=1, value=item.question_index + 1)
        ws.cell(row=idx, column=2, value=item.question_text)
        ws.cell(row=idx, column=3, value=item.final_answer or item.suggested_answer or "")
        ws.cell(row=idx, column=4, value=item.status)

    # Auto-width columns
    ws.column_dimensions["B"].width = 60
    ws.column_dimensions["C"].width = 80
    ws.column_dimensions["D"].width = 15

    buffer = io.BytesIO()
    wb.save(buffer)
    buffer.seek(0)

    filename = original_filename.rsplit(".", 1)[0] + "_filled.xlsx"
    return buffer.read(), filename, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
