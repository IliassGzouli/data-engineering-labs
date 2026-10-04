import logging
from requests.exceptions import HTTPError

import argparse

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

    parser = argparse.ArgumentParser(
        description="Run the NYC Taxi monthly pipeline."
    )

    parser.add_argument(
        "--year",
        type=int,
        required=True,
    )

    parser.add_argument(
        "--month",
        type=int,
        required=True,
    )

    args = parser.parse_args()

    run_monthly_pipeline(
        year=args.year,
        month=args.month,
    )



