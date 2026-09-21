import logging

from ingestion.extract import configure_logging, download_yellow_taxi_data
from ingestion.load_raw import load_raw_parquet
from ingestion.validate import validate_table
from cloud.s3 import upload_file_to_s3
from config.cloud import S3_BUCKET_NAME

logger = logging.getLogger(__name__)

def run_ingestion_pipeline(year: int, month: int) -> None:
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

    upload_file_to_s3(
        local_path=parquet_path,
        bucket_name=S3_BUCKET_NAME,
        object_key=f"raw/{parquet_path.name}",
    )

    logger.info(
        "Ingestion pipeline completed successfully for %04d-%02d",
        year,
        month,
    )

if __name__ == "__main__":
    configure_logging()

    run_ingestion_pipeline(
        year=2026,
        month=1,
    )