import logging

import boto3

from config.cloud import AWS_REGION


logger = logging.getLogger(__name__)


def start_glue_crawler(crawler_name: str) -> None:
    """
    Start an AWS Glue crawler.

    Args:
        crawler_name: Name of the Glue crawler to start.
    """

    if not crawler_name:
        raise ValueError("crawler_name must not be empty")

    client = boto3.client(
        "glue",
        region_name=AWS_REGION,
    )

    logger.info(
        "Starting Glue crawler: %s",
        crawler_name,
    )

    client.start_crawler(
        Name=crawler_name,
    )