"""Read allowlisted SVG assets from MinIO or local development storage."""

import asyncio
import os
import re

from app.core.config import ASSETS


class StorageUnavailableError(Exception):
    """Object storage could not serve an existing asset."""


def read_asset(name: str, storage) -> bytes:
    if (
        not re.fullmatch(r"asset-\d+(?:-peach|-turquoise)?\.svg", name)
        or not (ASSETS / name).is_file()
    ):
        raise FileNotFoundError(name)
    if storage:
        try:
            obj = storage.get_object(Bucket=os.getenv("S3_BUCKET", "illustrations"), Key=name)
            body = obj["Body"]
            data = body.read()
            body.close()
        except Exception as error:
            raise StorageUnavailableError() from error
    else:
        data = (ASSETS / name).read_bytes()
    return data


async def initialize_storage():
    """Connect to MinIO and seed the prepared library at startup."""
    import boto3
    from botocore.config import Config

    s3 = boto3.client(
        "s3",
        endpoint_url=os.environ["S3_ENDPOINT"],
        aws_access_key_id=os.environ["S3_ACCESS_KEY"],
        aws_secret_access_key=os.environ["S3_SECRET_KEY"],
        region_name="us-east-1",
        config=Config(connect_timeout=5, read_timeout=10, retries={"max_attempts": 2}),
    )
    bucket = os.getenv("S3_BUCKET", "illustrations")
    try:
        await asyncio.to_thread(s3.head_bucket, Bucket=bucket)
    except Exception:
        await asyncio.to_thread(s3.create_bucket, Bucket=bucket)
    for p in ASSETS.glob("*.svg"):
        await asyncio.to_thread(
            s3.put_object,
            Bucket=bucket,
            Key=p.name,
            Body=p.read_bytes(),
            ContentType="image/svg+xml",
        )
    return s3
