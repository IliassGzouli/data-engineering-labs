import logging
from pathlib import Path

from ingestion.load_raw import load_raw_parquet
from transformation.load_processed import save_processed_parquet
from transformation.load_quality import save_quality_outputs
from transformation.quarantine import split_valid_and_quarantine
from transformation.transform import transform_trips

logger = logging.getLogger(__name__)


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

    # 2. Transform
    transformed_table = transform_trips(table)

    # 3. Save processed
    processed_path = save_processed_parquet(
        table=transformed_table,
        filename=input_path.name,
    )

    # 4. Split quality
    valid_table, quarantine_table = split_valid_and_quarantine(
        transformed_table
    )

    # 5. Save valid + quarantine
    valid_path, quarantine_path = save_quality_outputs(
        valid_table=valid_table,
        quarantine_table=quarantine_table,
        filename=input_path.name,
    )

    logger.info(
        "Transformation pipeline completed successfully"
    )

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