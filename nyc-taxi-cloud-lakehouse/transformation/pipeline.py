import logging
from pathlib import Path

from ingestion.load_raw import load_raw_parquet
from ingestion.validate import validate_table
from transformation.load_processed import save_processed_parquet
from transformation.load_quality import save_quality_outputs
from transformation.quarantine import split_valid_and_quarantine
from transformation.transform import transform_trips

from cloud.s3 import s3_object_exists, upload_file_to_s3
from config.cloud import (S3_BUCKET_NAME,GLUE_PROCESSED_CRAWLER_NAME,GLUE_QUARANTINE_CRAWLER_NAME,GLUE_VALID_CRAWLER_NAME)
from cloud.glue import start_glue_crawler

logger = logging.getLogger(__name__)

def extract_year_month(filename: str) -> tuple[int, int]:
    """
    Extract year and month from a NYC Taxi filename.

    Example:
        yellow_tripdata_2026-01.parquet
        -> (2026, 1)
    """

    stem = Path(filename).stem
    year_month = stem.split("_")[-1]

    year_str, month_str = year_month.split("-")
    return int(year_str), int(month_str)


def run_transformation_pipeline(
    input_path: Path,
) -> tuple[Path, Path, Path]:
    """
    Run the transformation and quality pipeline.

    Returns:
        processed_path,
        valid_path,
        quarantine_path
    """

    logger.info(
        "Starting transformation pipeline for %s",
        input_path,
    )

    # 1. Load raw
    table = load_raw_parquet(input_path)

    # 2. Validate raw data
    validate_table(table)

    # 3. Transform
    transformed_table = transform_trips(table)

    # 4. Save processed
    processed_path = save_processed_parquet(
        table=transformed_table,
        filename=input_path.name,
    )

    # 5. Split valid / quarantine
    valid_table, quarantine_table = split_valid_and_quarantine(
        transformed_table
    )

    # 6. Save valid + quarantine
    valid_path, quarantine_path = save_quality_outputs(
        valid_table=valid_table,
        quarantine_table=quarantine_table,
        filename=input_path.name,
    )

    # 7. Extract year and month for S3 partitioning
    year, month = extract_year_month(input_path.name)
    
    # 8. Build S3 object keys
    processed_key = (
        f"processed/"
        f"year={year}/"
        f"month={month:02d}/"
        f"{processed_path.name}"
    )

    valid_key = (
        f"quality/valid/"
        f"year={year}/"
        f"month={month:02d}/"
        f"{valid_path.name}"
    )

    quarantine_key = (
        f"quality/quarantine/"
        f"year={year}/"
        f"month={month:02d}/"
        f"{quarantine_path.name}"
    )

    uploaded_any = False

    # 9. Upload processed if missing
    if s3_object_exists(
        bucket_name=S3_BUCKET_NAME,
        object_key=processed_key,
    ):
        logger.info(
            "Processed object already exists in S3, skipping upload: s3://%s/%s",
            S3_BUCKET_NAME,
            processed_key,
        )
    else:
        upload_file_to_s3(
            local_path=processed_path,
            bucket_name=S3_BUCKET_NAME,
            object_key=processed_key,
        )
        uploaded_any = True

    # 10. Upload valid if missing
    if s3_object_exists(
        bucket_name=S3_BUCKET_NAME,
        object_key=valid_key,
    ):
        logger.info(
            "Valid object already exists in S3, skipping upload: s3://%s/%s",
            S3_BUCKET_NAME,
            valid_key,
        )
    else:
        upload_file_to_s3(
            local_path=valid_path,
            bucket_name=S3_BUCKET_NAME,
            object_key=valid_key,
        )
        uploaded_any = True

    # 11. Upload quarantine if missing
    if s3_object_exists(
        bucket_name=S3_BUCKET_NAME,
        object_key=quarantine_key,
    ):
        logger.info(
            "Quarantine object already exists in S3, skipping upload: s3://%s/%s",
            S3_BUCKET_NAME,
            quarantine_key,
        )
    else:
        upload_file_to_s3(
            local_path=quarantine_path,
            bucket_name=S3_BUCKET_NAME,
            object_key=quarantine_key,
        )
        uploaded_any = True


    logger.info(
        "Processed: %s",
        processed_path,
    )

    logger.info(
        "Valid: %s",
        valid_path,
    )

    logger.info(
        "Quarantine: %s",
        quarantine_path,
    )


    # Start Glue crawlers only when new S3 objects were uploaded
    if uploaded_any:
        logger.info(
            "New S3 objects uploaded, starting Glue crawlers"
        )

        start_glue_crawler(GLUE_PROCESSED_CRAWLER_NAME)
        start_glue_crawler(GLUE_VALID_CRAWLER_NAME)
        start_glue_crawler(GLUE_QUARANTINE_CRAWLER_NAME)

        logger.info("Glue crawlers started")
    else:
        logger.info(
            "No new S3 objects uploaded, skipping Glue crawlers"
        )

    logger.info(
        "Transformation pipeline completed successfully"
    )

    return (
        processed_path,
        valid_path,
        quarantine_path,
    )


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )

    run_transformation_pipeline(
        Path("data/raw/yellow_tripdata_2026-01.parquet")
    )