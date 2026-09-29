import logging

from ingestion.pipeline import run_ingestion_pipeline
from transformation.pipeline import run_transformation_pipeline


logger = logging.getLogger(__name__)


def run_monthly_pipeline(
    year: int,
    month: int,
) -> None:
    logger.info(
        "Starting monthly pipeline for %04d-%02d",
        year,
        month,
    )

    raw_path = run_ingestion_pipeline(
        year=year,
        month=month,
    )

    run_transformation_pipeline(
        raw_path
    )

    logger.info(
        "Monthly pipeline completed successfully for %04d-%02d",
        year,
        month,
    )


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )

    run_monthly_pipeline(
        year=2026,
        month=2,
    )