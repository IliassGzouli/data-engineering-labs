import logging 
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq

logger = logging.getLogger(__name__)

VALID_DATA_PATH = Path("data/valid")
QUARANTINE_DATA_PATH = Path("data/quarantine")

def save_quality_outputs(
        valid_table: pa.Table,
        quarantine_table: pa.Table,
        filename: str,
        valid_data_dir: Path = VALID_DATA_PATH,
        quarantine_data_dir: Path = QUARANTINE_DATA_PATH
) -> tuple[Path, Path]:
    """
    Save valid and quarantined NYC Taxi rows
    into separate Parquet files.
    """

    valid_data_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    quarantine_data_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    valid_path = valid_data_dir / filename
    quarantine_path = quarantine_data_dir / filename

    logger.info(
        "Saving valid data: %s",
        valid_path,
    )

    try:
        pq.write_table(
            valid_table,
            valid_path,
            compression="snappy",
        )

        logger.info(
            "Saving quarantine data: %s",
            quarantine_path,
        )

        pq.write_table(
            quarantine_table,
            quarantine_path,
            compression="snappy",
        )

    except (OSError, pa.ArrowException) as exc:
        logger.error(
            "Failed to save quality outputs: %s",
            exc,
        )
        raise

    logger.info(
        "Quality outputs saved successfully: "
        "%s valid rows, %s quarantined rows",
        f"{valid_table.num_rows:,}",
        f"{quarantine_table.num_rows:,}",
    )

    return valid_path, quarantine_path