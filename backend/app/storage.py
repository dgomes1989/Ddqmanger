"""File storage using Supabase Storage."""

import uuid

from supabase import create_client

from app.config import settings


def get_supabase_client():
    return create_client(settings.supabase_url, settings.supabase_key)


async def upload_file(file_content: bytes, filename: str, content_type: str) -> str:
    """Upload a file to Supabase Storage and return the storage path."""
    client = get_supabase_client()
    file_key = f"uploads/{uuid.uuid4()}/{filename}"
    client.storage.from_(settings.supabase_storage_bucket).upload(
        path=file_key,
        file=file_content,
        file_options={"content-type": content_type},
    )
    return file_key


async def download_file(file_path: str) -> bytes:
    """Download a file from Supabase Storage."""
    client = get_supabase_client()
    response = client.storage.from_(settings.supabase_storage_bucket).download(file_path)
    return response


async def delete_file(file_path: str):
    """Delete a file from Supabase Storage."""
    client = get_supabase_client()
    client.storage.from_(settings.supabase_storage_bucket).remove([file_path])
