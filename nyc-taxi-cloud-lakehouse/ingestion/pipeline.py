import logging
from pathlib import Path

from ingestion.extract import configure_logging, download_yellow_taxi_data
from ingestion.load_raw import load_raw_parquet
from ingestion.validate import validate_table
from cloud.s3 import upload_file_to_s3, s3_object_exists
from config.cloud import S3_BUCKET_NAME

logger = logging.getLogger(__name__)

def run_ingestion_pipeline(year: int, month: int) -> Path:
    logger.info(
        "Starting ingestion pipeline for %04d-%02d",
        year,
        month,
    )

    parquet_path = download_yellow_taxi_data(
        year=year,
        month=month,
    )

    table = load_raw_parquet(parquet_path)

    validate_table(table)

    object_key = (
        f"raw/yellow/"
        f"year={year}/"
        f"month={month:02d}/"
        f"{parquet_path.name}"
    )

    if s3_object_exists(
        bucket_name=S3_BUCKET_NAME,
        object_key=object_key,
    ):
        logger.info(
            "Raw object already exists in S3, skipping upload: s3://%s/%s",
            S3_BUCKET_NAME,
            object_key,
        )
    else:
        upload_file_to_s3(
            local_path=parquet_path,
            bucket_name=S3_BUCKET_NAME,
            object_key=object_key,
        )
    logger.info(
        "Ingestion pipeline completed successfully for %04d-%02d",
        year,
        month,
    )
    return parquet_path

if __name__ == "__main__":
    configure_logging()

    run_ingestion_pipeline(
        year=2026,
        month=1,
    )