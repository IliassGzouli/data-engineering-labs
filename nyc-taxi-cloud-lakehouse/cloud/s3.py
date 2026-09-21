import logging
from pathlib import Path

import boto3
from boto3.s3.transfer import TransferConfig
from botocore.config import Config
from botocore.exceptions import BotoCoreError, ClientError

from config.cloud import AWS_REGION

logger = logging.getLogger(__name__)

TRANSFER_CONFIG = TransferConfig(
    multipart_threshold=8 * 1024 * 1024,
    multipart_chunksize=16 * 1024 * 1024,
    max_concurrency=2,
    use_threads=True,
)


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

    client_config = Config(
        region_name=AWS_REGION,
        connect_timeout=10,
        read_timeout=300,
        tcp_keepalive=True,
        retries={
            "max_attempts": 5,
            "mode": "standard",
        },
    )

    s3_client = boto3.client(
        "s3",
        config=client_config,
    )

    try:
        s3_client.upload_file(
            str(local_path),
            bucket_name,
            object_key,
            Config=TRANSFER_CONFIG,
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