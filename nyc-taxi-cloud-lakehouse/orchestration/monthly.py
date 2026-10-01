import logging
from requests.exceptions import HTTPError

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


def run_backfill(
    year: int,
    start_month: int,
    end_month: int,
) -> None:
    for month in range(start_month, end_month + 1):
        logger.info(
            "Starting backfill for %04d-%02d",
            year,
            month,
        )

        try:
            run_monthly_pipeline(
                year=year,
                month=month,
            )

        except HTTPError as exc:
            logger.warning(
                "Source unavailable for %04d-%02d, skipping: %s",
                year,
                month,
                exc,
            )
            continue

        logger.info(
            "Backfill completed for %04d-%02d",
            year,
            month,
        )

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )

    run_backfill(
        year=2026,
        start_month=4,
        end_month=8,
    )



