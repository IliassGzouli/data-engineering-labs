import os


S3_BUCKET_NAME = os.getenv(
    "S3_BUCKET_NAME",
    "iliass-nyc-taxi-lakehouse-2026",
)

AWS_REGION = os.getenv(
    "AWS_REGION",
    "us-east-1",
)

GLUE_PROCESSED_CRAWLER_NAME = os.getenv(
    "GLUE_PROCESSED_CRAWLER_NAME",
    "nyc-taxi-processed-crawler",
)

GLUE_VALID_CRAWLER_NAME = os.getenv(
    "GLUE_VALID_CRAWLER_NAME",
    "nyc-taxi-valid-crawler",
)

GLUE_QUARANTINE_CRAWLER_NAME = os.getenv(
    "GLUE_QUARANTINE_CRAWLER_NAME",
    "nyc-taxi-quarantine-crawler",
)