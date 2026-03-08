import uuid

import boto3
from botocore.config import Config

from app.config import settings


def get_s3_client():
    return boto3.client(
        "s3",
        endpoint_url=settings.s3_endpoint_url,
        aws_access_key_id=settings.s3_access_key,
        aws_secret_access_key=settings.s3_secret_key,
        config=Config(signature_version="s3v4"),
        region_name="us-east-1",
    )


def ensure_bucket():
    client = get_s3_client()
    try:
        client.head_bucket(Bucket=settings.s3_bucket_name)
    except Exception:
        client.create_bucket(Bucket=settings.s3_bucket_name)


async def upload_file(file_content: bytes, filename: str, content_type: str) -> str:
    """Upload a file to S3 and return the storage path."""
    client = get_s3_client()
    file_key = f"uploads/{uuid.uuid4()}/{filename}"
    client.put_object(
        Bucket=settings.s3_bucket_name,
        Key=file_key,
        Body=file_content,
        ContentType=content_type,
    )
    return file_key


async def download_file(file_path: str) -> bytes:
    """Download a file from S3."""
    client = get_s3_client()
    response = client.get_object(Bucket=settings.s3_bucket_name, Key=file_path)
    return response["Body"].read()


async def delete_file(file_path: str):
    """Delete a file from S3."""
    client = get_s3_client()
    client.delete_object(Bucket=settings.s3_bucket_name, Key=file_path)
