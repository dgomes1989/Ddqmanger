"""Generate embeddings for semantic search using Anthropic's Voyage AI."""

import anthropic

from app.config import settings


async def generate_embedding(text: str) -> list[float]:
    """Generate an embedding vector for a text string."""
    client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)

    # Use Voyage AI embeddings via Anthropic
    # For now, use a simple approach with Claude to generate a normalized text
    # In production, you'd use Voyage AI or another embedding model
    # Placeholder: using Anthropic's recommended embedding approach

    try:
        import httpx

        voyage_client = httpx.AsyncClient()
        response = await voyage_client.post(
            "https://api.voyageai.com/v1/embeddings",
            headers={"Authorization": f"Bearer {settings.anthropic_api_key}"},
            json={
                "input": [text[:8000]],  # Voyage limit
                "model": "voyage-3",
            },
        )
        await voyage_client.aclose()

        if response.status_code == 200:
            data = response.json()
            return data["data"][0]["embedding"]
    except Exception:
        pass

    # Fallback: return None to skip embedding-based search
    return []


async def generate_embeddings_batch(texts: list[str]) -> list[list[float]]:
    """Generate embeddings for a batch of texts."""
    results = []
    # Process in batches of 8
    batch_size = 8
    for i in range(0, len(texts), batch_size):
        batch = texts[i : i + batch_size]
        for text in batch:
            embedding = await generate_embedding(text)
            results.append(embedding)
    return results
