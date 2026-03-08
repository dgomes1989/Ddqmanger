"""Extract question-answer pairs from document text using Claude."""

import json

import anthropic

from app.config import settings

QA_EXTRACTION_PROMPT = """You are analyzing a Due Diligence Questionnaire (DDQ) or investment-related document.
Extract all question-answer pairs from the following text.

For each pair, provide:
- "question": The question text (clean it up if needed)
- "answer": The answer text (if present, otherwise null)
- "category": A category for the question (e.g., "Fund Overview", "Investment Strategy", "Risk Management", "Operations", "Legal & Compliance", "Performance", "Team", "ESG", "Fees", "Other")

Return a JSON array of objects. If the document only contains questions without answers (an unfilled DDQ), set answer to null.

IMPORTANT: Return ONLY the JSON array, no other text.

Document text:
{text}"""

QUESTIONS_ONLY_PROMPT = """You are analyzing a Due Diligence Questionnaire (DDQ) or investment request document.
Extract ALL questions from the following text. These are questions that need to be answered.

For each question, provide:
- "question": The question text (clean it up if needed)
- "category": A category for the question (e.g., "Fund Overview", "Investment Strategy", "Risk Management", "Operations", "Legal & Compliance", "Performance", "Team", "ESG", "Fees", "Other")

Return a JSON array of objects. Return ONLY the JSON array, no other text.

Document text:
{text}"""


async def extract_qa_pairs(text: str) -> list[dict]:
    """Extract question-answer pairs from document text using Claude."""
    client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)

    # Truncate very long documents to fit context window
    max_chars = 150000
    if len(text) > max_chars:
        text = text[:max_chars]

    message = await client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=8192,
        messages=[
            {"role": "user", "content": QA_EXTRACTION_PROMPT.format(text=text)}
        ],
    )

    response_text = message.content[0].text.strip()

    # Parse JSON from response (handle markdown code blocks)
    if response_text.startswith("```"):
        response_text = response_text.split("\n", 1)[1].rsplit("```", 1)[0].strip()

    return json.loads(response_text)


async def extract_questions_only(text: str) -> list[dict]:
    """Extract only questions from an unfilled DDQ."""
    client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)

    max_chars = 150000
    if len(text) > max_chars:
        text = text[:max_chars]

    message = await client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=8192,
        messages=[
            {"role": "user", "content": QUESTIONS_ONLY_PROMPT.format(text=text)}
        ],
    )

    response_text = message.content[0].text.strip()
    if response_text.startswith("```"):
        response_text = response_text.split("\n", 1)[1].rsplit("```", 1)[0].strip()

    return json.loads(response_text)
