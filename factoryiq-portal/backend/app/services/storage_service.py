import boto3
from botocore.client import Config
from app.core.config import settings


def client():
    return boto3.client(
        "s3",
        endpoint_url=f"http://{settings.minio_endpoint}",
        aws_access_key_id=settings.minio_access_key,
        aws_secret_access_key=settings.minio_secret_key,
        config=Config(signature_version="s3v4"),
        region_name="us-east-1",
    )


def put_object(key: str, content: bytes):
    s3 = client()
    s3.put_object(Bucket=settings.minio_bucket, Key=key, Body=content)


def presigned_download(key: str) -> str:
    s3 = client()
    return s3.generate_presigned_url(
        "get_object",
        Params={"Bucket": settings.minio_bucket, "Key": key},
        ExpiresIn=3600,
    )
