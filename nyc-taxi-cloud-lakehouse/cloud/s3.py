import logging
from pathlib import Path

import boto3
from botocore.exceptions import BotoCoreError, ClientError

logger = logging.getLogger(__name__)


def upload_file_to_s3(
    local_path: Path,
    bucket_name: str,
    object_key: str,
) -> None:
    """
    Upload a local file to Amazon S3.
    """

    if not local_path.exists():
        raise FileNotFoundError(
            f"Local file not found: {local_path}"
        )

    if not local_path.is_file():
        raise ValueError(
            f"Path is not a file: {local_path}"
        )

    logger.info(
        "Uploading %s to s3://%s/%s",
        local_path,
        bucket_name,
        object_key,
    )

    s3_client = boto3.client("s3")

    try:
        s3_client.upload_file(
            str(local_path),
            bucket_name,
            object_key,
        )

    except (BotoCoreError, ClientError) as exc:
        logger.error(
            "Failed to upload file to S3: %s",
            exc,
        )
        raise

    logger.info(
        "Upload completed successfully: s3://%s/%s",
        bucket_name,
        object_key,
    )