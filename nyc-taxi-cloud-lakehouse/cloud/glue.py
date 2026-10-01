import logging

import boto3

from config.cloud import AWS_REGION


logger = logging.getLogger(__name__)


def start_glue_crawler(crawler_name: str) -> None:
    """
    Start an AWS Glue crawler.

    If the crawler is already running, skip it safely.

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

    try:
        client.start_crawler(
            Name=crawler_name,
        )

    except client.exceptions.CrawlerRunningException:
        logger.info(
            "Glue crawler already running, skipping: %s",
            crawler_name,
        )