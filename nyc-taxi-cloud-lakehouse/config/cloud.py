import os


S3_BUCKET_NAME = os.getenv(
    "S3_BUCKET_NAME",
    "iliass-nyc-taxi-lakehouse-2026",
)

AWS_REGION = os.getenv(
    "AWS_REGION",
    "us-east-1",
)