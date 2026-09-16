import logging
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq

logger = logging.getLogger(__name__)

def load_raw_parquet(path: Path) -> pa.Table:
    """
    Load a raw Parquet file into a PyArrow Table.
    """

    if not path.exists():
        raise FileNotFoundError(
            f"Raw Parquet file not found: {path}"
        )

    if not path.is_file():
        raise ValueError(
            f"Path is not a file: {path}"
        )

    logger.info(
        "Loading raw Parquet file: %s",
        path,
    )

    try:
        table = pq.read_table(path)

    except (OSError, pa.ArrowException) as exc:
        logger.error(
            "Failed to load Parquet file %s: %s",
            path,
            exc,
        )

        raise

    logger.info(
        "Raw Parquet loaded successfully: %s rows, %s columns",
        f"{table.num_rows:,}",
        table.num_columns,
    )
    return table